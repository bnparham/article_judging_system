from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from schedule.models import Schedule
from account.models import Teacher
from itertools import chain

def filter_supervisors(request, schedule_id, sessionId):
    schedule = get_object_or_404(Schedule, id=schedule_id)

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