from django.contrib import admin

from .models import Attendance, AttendanceDay, Member, MemberJob, Shift, ShiftDuration

# Register your models here.


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberJob)
class MemberJobAdmin(admin.ModelAdmin):
    pass


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    pass


@admin.register(ShiftDuration)
class ShiftHoursAdmin(admin.ModelAdmin):
    pass


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    pass


@admin.register(AttendanceDay)
class AttendanceDayAdmin(admin.ModelAdmin):
    pass
