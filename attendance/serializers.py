from datetime import datetime, timedelta
import pytz
from rest_framework import serializers
from .models import Attendance, AttendanceDay, Member, MemberJob, Shift, ShiftDuration


SHIFT_DURATION_LIMIT = 16 * (60 * 60)


class DAYS:
    SUN = "Sunday"
    MON = "Monday"
    TUES = "Tuesday"
    WED = "Wednesday"
    THURS = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"


def isWorkDay(shift, day):
    if day == DAYS.SUN:
        return shift.sun
    if day == DAYS.MON:
        return shift.mon
    if day == DAYS.TUES:
        return shift.tues
    if day == DAYS.WED:
        return shift.wed
    if day == DAYS.THURS:
        return shift.thurs
    if day == DAYS.FRI:
        return shift.fri
    if day == DAYS.SAT:
        return shift.sat

    return False


class ShiftDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftDuration
        fields = '__all__'


class MemberJobSerialzer(serializers.ModelSerializer):
    class Meta:
        model = MemberJob
        fields = ['id', 'label']


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'member', 'current_date',
                  'start_datetime', 'end_datetime', 'is_dayoff', 'shift', 'shift_duration', 'local_ip']

    shift = ShiftSerializer()
    shift_duration = serializers.SlugRelatedField(
        read_only=True, slug_field='duration')
    current_date = serializers.SlugRelatedField(
        read_only=True, slug_field='day')

    shift_duration = serializers.SerializerMethodField(
        method_name='shift_duration_to_int')

    def shift_duration_to_int(self, member: Member):
        return int(member.shift_duration.duration.seconds)


class AttendanceCUDSerializer(AttendanceSerializer):
    current_date = None


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'user', 'full_name', 'email',
                  'is_admin', 'job', 'shift', 'shift_duration']

    full_name = serializers.SlugRelatedField(read_only=True,
                                             slug_field='full_name', source='user')
    email = serializers.SlugRelatedField(read_only=True,
                                         slug_field='email', source='user')
    is_admin = serializers.SlugRelatedField(read_only=True,
                                            slug_field='is_staff', source='user')

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    job = serializers.StringRelatedField()
    shift = ShiftSerializer(read_only=True)

    shift_duration = serializers.SerializerMethodField(
        method_name='shift_duration_to_int')

    def shift_duration_to_int(self, member: Member):
        return int(member.shift_duration.duration.seconds)


class FullMemberSerializer(MemberSerializer):
    class Meta:
        model = Member
        fields = ['id', 'user', 'full_name', 'email',
                  'is_admin', 'job', 'shift', 'shift_duration', 'attendance_set', 'total_work_time', 'attended_time', 'attended_days',]
        # 'day_offs', 'vacations']

    shift_duration = serializers.SerializerMethodField(
        method_name='shift_duration_to_int')

    attendance_set = AttendanceSerializer(many=True)

    def shift_duration_to_int(self, member: Member):
        return int(member.shift_duration.duration.seconds)

    def to_representation(self, member: Member):
        data = super().to_representation(member)
        data['total_work_days'] = int(data.get(
            'total_work_time') / (60 * 60 * member.shift_duration.duration.seconds / (60 * 60)))
        return data

    total_work_time = serializers.SerializerMethodField(
        method_name='cacluate_total_work_time')

    attended_time = serializers.SerializerMethodField(
        method_name='cacluate_attended_time')
    attended_days = serializers.SerializerMethodField(
        method_name='cacluate_attended_days')
    # day_offs = serializers.SerializerMethodField(
    #     method_name='cacluate_day_offs')
    # vacations = serializers.SerializerMethodField(
    #     method_name='cacluate_vacations')

    def cacluate_total_work_time(self, member: Member):
        duration = member.shift_duration.duration.seconds
        total_duration = 0
        dayoffs = member.attendance_set.select_related(
            'current_date').select_related('shift_duration').filter(current_date__day__gte=self.context['min_date'], current_date__day__lte=self.context['max_date'], is_dayoff=True)

        for i in range((self.context['max_date'] - self.context['min_date']).days + 1):
            day = self.context['min_date'] + timedelta(days=i)
            if not isWorkDay(member.shift, day.strftime('%A')):
                continue
            total_duration += duration

        vacations_count = 0
        for attendance in dayoffs:
            if isWorkDay(member.shift, attendance.current_date.day.strftime('%A')):
                vacations_count += 1
        return int(total_duration - vacations_count * duration)

    def cacluate_attended_time(self, member: Member):
        months_attendances = member.attendance_set.select_related('current_date').select_related('shift_duration').filter(
            current_date__day__gte=self.context['min_date'], current_date__day__lte=self.context['max_date'])
        total_duration = 0
        for attendance in months_attendances:
            duration = attendance.shift_duration.duration.seconds
            if attendance.end_datetime == None:
                diff = (datetime.now().astimezone(pytz.utc)
                        - attendance.start_datetime.astimezone(pytz.utc))
                if diff >= timedelta(seconds=SHIFT_DURATION_LIMIT):
                    diff = timedelta(seconds=duration / 2)
                total_duration += diff.total_seconds()
            else:
                total_duration += (attendance.end_datetime -
                                   attendance.start_datetime).total_seconds()
        return int(total_duration)

    def cacluate_attended_days(self, member: Member):
        return member.attendance_set.select_related('current_date').filter(
            current_date__day__gte=self.context['min_date'], current_date__day__lte=self.context['max_date']).count()

    # def cacluate_day_offs(self, member: Member):
    #     day_offs_count = member.attendance_set.select_related('current_date').filter(
    #         current_date__day__gte=self.context['min_date'], current_date__day__lte=self.context['max_date'], is_dayoff=True).count()
    #     for i in range((self.context['max_date'] - self.context['min_date']).days + 1):
    #         day = self.context['min_date'] + timedelta(days=i)
    #         if not isWorkDay(member.shift, day.strftime('%A')):
    #             continue

    #     return day_offs_count

    # def cacluate_vacations(self, member: Member):
    #     dayoffs = member.attendance_set.select_related(
    #         'current_date').select_related('shift_duration').filter(current_date__day__gte=self.context['min_date'], current_date__day__lte=self.context['max_date'], is_dayoff=True)

    #     dayoffs_count = 0
    #     for i in range((self.context['max_date'] - self.context['min_date']).days + 1):
    #         day = self.context['min_date'] + timedelta(days=i)
    #         if not isWorkDay(member.shift, day.strftime('%A')):
    #             dayoffs_count += 1

    #     vacations_count = 0
    #     for attendance in dayoffs:
    #         if isWorkDay(member.shift, attendance.current_date.day.strftime('%A')):
    #             vacations_count += 1
    #     return vacations
