from django.db import models
from django.conf import settings

# Create your models here.


class MemberJob(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label


class Shift(models.Model):
    sun = models.BooleanField(default=False)
    mon = models.BooleanField(default=False)
    tues = models.BooleanField(default=False)
    wed = models.BooleanField(default=False)
    thurs = models.BooleanField(default=False)
    fri = models.BooleanField(default=False)
    sat = models.BooleanField(default=False)

    def __str__(self) -> str:
        return ", ".join(filter(lambda x: x, [
            "sun" if self.sun else "",
            "mon" if self.mon else "",
            "tues" if self.tues else "",
            "wed" if self.wed else "",
            "thurs" if self.thurs else "",
            "fri" if self.fri else "",
            "sat" if self.sat else "",
        ]))


class ShiftDuration(models.Model):
    duration = models.DurationField()

    def __str__(self) -> str:
        total_seconds = self.duration.total_seconds()
        total_minutes = total_seconds // 60
        total_hours = int(total_minutes // 60)

        remaining_minutes = int(total_minutes % 60)
        remaining_seconds = int(total_seconds % 60)

        return f"{total_hours} hours, {remaining_minutes} minutes, {remaining_seconds} seconds"


class Member(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(MemberJob, on_delete=models.RESTRICT)
    shift = models.ForeignKey(Shift, on_delete=models.RESTRICT)
    shift_duration = models.ForeignKey(
        ShiftDuration, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return self.user.full_name


class AttendanceDay(models.Model):
    day = models.DateField(auto_now_add=True, unique=True)

    def __str__(self) -> str:
        return self.day.isoformat()


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.RESTRICT)
    shift_duration = models.ForeignKey(
        ShiftDuration, on_delete=models.RESTRICT)
    current_date = models.ForeignKey(AttendanceDay, on_delete=models.RESTRICT)
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)
    is_dayoff = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'current_date')

    def __str__(self) -> str:
        return self.member.user.full_name + f" ({self.current_date.day.strftime('%A, %B %d, %Y')})"
