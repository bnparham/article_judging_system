from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from schedule.models import Schedule
from account.models import Teacher
from itertools import chain

def filter_supervisors(request, schedule_id, sessionId):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if sessionId == 'add':
        # Query supervisors not assigned to the same schedule in other sessions
        supervisors_not_in_other_sessions = Teacher.objects.filter(
            ~Q(supervisor1_assignments__schedule=schedule) &
            ~Q(supervisor2_assignments__schedule=schedule) &
            ~Q(supervisor3_assignments__schedule=schedule) &
            ~Q(supervisor4_assignments__schedule=schedule)
        )
        combined_supervisors = list(chain(supervisors_not_in_other_sessions))
        unique_supervisors = {supervisor.id: supervisor for supervisor in combined_supervisors}.values()
    else:
        # Query supervisors assigned to the current session's schedule
        supervisors_in_current_session = Teacher.objects.filter(
            Q(supervisor1_assignments__schedule=schedule, supervisor1_assignments__id=sessionId) |
            Q(supervisor2_assignments__schedule=schedule, supervisor2_assignments__id=sessionId) |
            Q(supervisor3_assignments__schedule=schedule, supervisor3_assignments__id=sessionId) |
            Q(supervisor4_assignments__schedule=schedule, supervisor4_assignments__id=sessionId)
        )

        # Query supervisors not assigned to the same schedule in other sessions
        supervisors_not_in_other_sessions = Teacher.objects.filter(
            ~Q(supervisor1_assignments__schedule=schedule) &
            ~Q(supervisor2_assignments__schedule=schedule) &
            ~Q(supervisor3_assignments__schedule=schedule) &
            ~Q(supervisor4_assignments__schedule=schedule)
        )

        # Combine results and remove duplicates
        combined_supervisors = list(chain(supervisors_in_current_session, supervisors_not_in_other_sessions))
        unique_supervisors = {supervisor.id: supervisor for supervisor in combined_supervisors}.values()

    # Prepare response with supervisor data
    supervisor_data = [{"id": supervisor.id, "name": supervisor.user.name} for supervisor in unique_supervisors]
    return JsonResponse({"supervisors": supervisor_data})

def filter_graduate_monitor(request, schedule_id, sessionId):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if sessionId == 'add':
        # Query graduateMonitors not assigned to the same schedule in other sessions
        graduateMonitors_not_in_other_sessions = Teacher.objects.filter(
            ~Q(graduate_monitor_assignments__schedule=schedule)
        )
        combined_graduateMonitors = list(chain(graduateMonitors_not_in_other_sessions))
        unique_graduateMonitors = {graduateMonitor.id: graduateMonitor for
                                   graduateMonitor in combined_graduateMonitors}.values()
    else:
        # Query graduateMonitors assigned to the current session's schedule
        graduateMonitors_in_current_session = Teacher.objects.filter(
            Q(graduate_monitor_assignments__schedule=schedule, graduate_monitor_assignments__id=sessionId)
        )

        # Query graduateMonitors not assigned to the same schedule in other sessions
        graduateMonitors_not_in_other_sessions = Teacher.objects.filter(
            ~Q(graduate_monitor_assignments__schedule=schedule)
        )

        # Combine results and remove duplicates
        combined_graduateMonitors = list(chain(graduateMonitors_in_current_session,
                                               graduateMonitors_not_in_other_sessions))
        unique_graduateMonitors = {graduateMonitor.id: graduateMonitor for graduateMonitor in combined_graduateMonitors}.values()

    # Prepare response with graduateMonitor data
    graduateMonitor_data = [{"id": graduateMonitor.id, "name": graduateMonitor.user.name} for
                            graduateMonitor in unique_graduateMonitors]
    return JsonResponse({"graduateMonitors": graduateMonitor_data})

def filter_judge(request, schedule_id, sessionId):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if sessionId == 'add':
        # Query supervisors not assigned to the same schedule in other sessions
        judges_not_in_other_sessions = Teacher.objects.filter(
            ~Q(judge1_assignments__schedule=schedule) &
            ~Q(judge2_assignments__schedule=schedule) &
            ~Q(judge3_assignments__schedule=schedule)
        )
        combined_judges = list(chain(judges_not_in_other_sessions))
        unique_judges = {judge.id: judge for judge in combined_judges}.values()
    else:
        # Query judges assigned to the current session's schedule
        judges_in_current_session = Teacher.objects.filter(
            Q(judge1_assignments__schedule=schedule, judge1_assignments__id=sessionId) |
            Q(judge2_assignments__schedule=schedule, judge2_assignments__id=sessionId) |
            Q(judge3_assignments__schedule=schedule, judge3_assignments__id=sessionId)
        )

        # Query judges not assigned to the same schedule in other sessions
        judges_not_in_other_sessions = Teacher.objects.filter(
            ~Q(judge1_assignments__schedule=schedule) &
            ~Q(judge2_assignments__schedule=schedule) &
            ~Q(judge3_assignments__schedule=schedule)
        )

        # Combine results and remove duplicates
        combined_judges = list(chain(judges_in_current_session, judges_not_in_other_sessions))
        unique_judges = {judge.id: judge for judge in combined_judges}.values()

    # Prepare response with judge data
    judge_data = [{"id": judge.id, "name": judge.user.name} for judge in unique_judges]
    return JsonResponse({"judges": judge_data})
