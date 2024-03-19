from datetime import datetime, date, timedelta
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
import pytz
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsControlOrAdmin, IsMemberOrControlOrAdmin
from .models import Attendance, AttendanceDay, Member, ShiftDuration
from .serializers import AttendanceCUDSerializer, AttendanceSerializer, FullMemberSerializer, MemberSerializer, ShiftDurationSerializer, isWorkDay
from .serializers import SHIFT_DURATION_LIMIT


class MemberViewSet(ModelViewSet):
    permission_classes = [IsMemberOrControlOrAdmin]

    def get_queryset(self):
        queryset = Member.objects.select_related('job').all()
        if IsControlOrAdmin().has_permission(self.request, self):
            queryset = queryset.select_related('user').select_related(
                'shift').select_related('shift_duration')
            attendance_queryset = Attendance.objects.select_related(
                'current_date').all()
            min_date = self.request.query_params.get('min_date')
            min_date = min_date if min_date else None
            if min_date != None:
                try:
                    min_date = date.fromisoformat(min_date)
                    attendance_queryset = attendance_queryset.filter(
                        current_date__day__gte=min_date)
                except ValueError:
                    min_date = None
                    pass
            max_date = self.request.query_params.get('max_date')
            max_date = max_date if max_date else None
            if max_date != None:
                try:
                    max_date = date.fromisoformat(max_date)
                    attendance_queryset = attendance_queryset.filter(
                        current_date__day__lte=max_date)
                except ValueError:
                    max_date = None
                    pass
            return queryset.prefetch_related(Prefetch('attendance_set', queryset=attendance_queryset))
        return queryset.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        min_date = self.request.query_params.get('min_date')
        min_date = min_date if min_date else None
        if min_date != None:
            try:
                min_date = date.fromisoformat(min_date)
            except ValueError:
                min_date = None
                pass

        max_date = self.request.query_params.get('max_date')
        max_date = max_date if max_date else None
        if max_date != None:
            try:
                max_date = date.fromisoformat(max_date)
            except ValueError:
                max_date = None
                pass

        if not min_date or not max_date:
            current_datetime = datetime.now()
            current_month = current_datetime.month
            current_year = current_datetime.year
            start_of_month = datetime(current_year, current_month, 1)
            end_of_month = datetime(
                current_year, current_month + 1, 1) - timedelta(days=1)
            return {
                'min_date': start_of_month,
                'max_date': end_of_month
            }
        return {
            'min_date': min_date,
            'max_date': max_date
        }

    def get_serializer_class(self):
        if IsControlOrAdmin().has_permission(self.request, self):
            return FullMemberSerializer
        return MemberSerializer

    @action(detail=False, methods=['GET'], permission_classes=[IsMemberOrControlOrAdmin])
    def me(self, request):
        member = Member.objects.get(user_id=request.user.id)
        serializer = MemberSerializer(member)
        return Response(serializer.data)


class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.select_related('current_date').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsControlOrAdmin]

    def get_serializer_class(self):
        return AttendanceSerializer if self.request.method in SAFE_METHODS else AttendanceCUDSerializer

    @action(detail=False, permission_classes=[IsMemberOrControlOrAdmin])
    def latest(self, request):
        member = Member.objects.get(user_id=request.user.id)
        try:
            latest_attendance = member.attendance_set.select_related(
                'current_date').latest('current_date__day')
        except Attendance.DoesNotExist:
            return Response({'detail': 'You Don\'t Have Any Attendances.'}, status=status.HTTP_404_NOT_FOUND)

        date = datetime.now().date()
        if date != latest_attendance.current_date.day:
            return Response({'detail': 'New Shift Exists.'}, status=status.HTTP_410_GONE)

        if latest_attendance.start_datetime and not latest_attendance.end_datetime:
            diff = (datetime.now().astimezone(pytz.utc) -
                    latest_attendance.start_datetime.astimezone(pytz.utc))
            if diff >= timedelta(seconds=SHIFT_DURATION_LIMIT):
                return Response({'detail': 'Shift Reached Duration Limit.'}, status=status.HTTP_410_GONE)

        serializer = AttendanceSerializer(latest_attendance)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=[IsMemberOrControlOrAdmin])
    def start(self, request):
        if not request.data.get('local_ip', None):
            return Response({'detail': 'Ip Address Was Not Provided.'}, status=status.HTTP_403_FORBIDDEN)

        member = Member.objects.get(user_id=request.user.id)
        date = datetime.now().date()

        (current_date, day_created) = AttendanceDay.objects.get_or_create(
            day=date)
        (attendance, attendance_created) = Attendance.objects.filter(
            current_date_id=current_date.pk).get_or_create(member_id=member.pk, current_date=current_date, shift=member.shift, shift_duration=member.shift_duration, local_ip=request.data['local_ip'], is_dayoff=(not isWorkDay(member.shift, date.strftime('%A'))))

        if attendance.start_datetime:
            return Response({'detail': 'You Already Started This Shift.'}, status=status.HTTP_403_FORBIDDEN)

        if attendance.end_datetime:
            return Response({'detail': 'This Shift Has Ended.'}, status=status.HTTP_410_GONE)

        attendance.start_datetime = datetime.now().astimezone(pytz.utc)
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=[IsMemberOrControlOrAdmin])
    def end(self, request):
        member = Member.objects.get(user_id=request.user.id)

        latest_attendance = member.attendance_set.select_related(
            'current_date').latest('current_date__day')

        if not latest_attendance:
            return Response({'detail': 'You Don\'t Have Any Attendances To End.'}, status=status.HTTP_404_NOT_FOUND)

        if latest_attendance.start_datetime and not latest_attendance.end_datetime:
            diff = (datetime.now().astimezone(pytz.utc) -
                    latest_attendance.start_datetime.astimezone(pytz.utc))
            if diff >= timedelta(seconds=SHIFT_DURATION_LIMIT):
                return Response({'detail': 'Shift Reached Duration Limit.'}, status=status.HTTP_410_GONE)

        current_date = datetime.now().date()
        try:
            current_date = AttendanceDay.objects.get(
                day=current_date)
            attendance = Attendance.objects.filter(
                current_date_id=current_date.pk).get(member_id=member.pk, current_date=current_date)
        except ObjectDoesNotExist:
            return Response({'detail': 'Please Start Your Attendance First.'}, status=status.HTTP_403_FORBIDDEN)

        if attendance.start_datetime == None:
            return Response({'detail': 'Please Start Your Attendance First.'}, status=status.HTTP_403_FORBIDDEN)

        if attendance.end_datetime != None:
            return Response({'detail': 'You Already Ended This Shift.'}, status=status.HTTP_403_FORBIDDEN)

        attendance.end_datetime = datetime.now().astimezone(pytz.utc)
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)


class ShiftHoursViewSet(ModelViewSet):
    queryset = ShiftDuration.objects.all()
    serializer_class = ShiftDurationSerializer

    def get_permissions(self):
        permissions = [IsMemberOrControlOrAdmin()]
        if self.request.method not in SAFE_METHODS:
            permissions += [IsControlOrAdmin()]
        return permissions
