"""
=========================================================
JOURNAL API MODULE
=========================================================

This module handles all Journal-related operations.

CURRENT ARCHITECTURE:
---------------------------------------------------------
We are transitioning from FUNCTION-BASED VIEWS → VIEWSETS

WHY THIS CHANGE?
---------------------------------------------------------
Old system (Function-based views):
- Manually wrote separate functions for CRUD
- Repeated permission and queryset logic
- Hard to scale in large applications
- More boilerplate code

New system (ViewSet-based):
- One class handles all CRUD operations
- DRF automatically generates endpoints
- Cleaner, scalable, production-style architecture
- Centralized logic (get_queryset, perform_create)

=========================================================
AUTH SYSTEM:
---------------------------------------------------------
- JWT Authentication is used
- Each request must include:
    Authorization: Bearer <access_token>

- User is automatically available as:
    request.user

=========================================================
DATA SECURITY MODEL:
---------------------------------------------------------
- Each journal belongs to a user (ForeignKey)
- Users can ONLY access their own journals
- Enforced via:
    1. queryset filtering (get_queryset)
    2. perform_create (auto-assign user)

=========================================================
"""



# =========================================================
# OLD FUNCTION-BASED VIEWS (LEGACY - COMMENTED OUT)
# KEPT FOR LEARNING PURPOSE ONLY
# =========================================================

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from journals.models import Journal
# from journals.serializers import JournalSerializer


# CREATE JOURNAL (OLD WAY)
# ---------------------------------------------------------
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_journal(request):
#     serializer = JournalSerializer(data=request.data)
#
#     if serializer.is_valid():
#         # IMPORTANT: user is assigned from backend (not frontend)
#         serializer.save(user=request.user)
#         return Response(serializer.data)
#
#     return Response(serializer.errors)


# GET USER'S JOURNALS (OLD WAY)
# ---------------------------------------------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def my_journals(request):
#     journals = Journal.objects.filter(user=request.user).order_by('-created_at')
#     serializer = JournalSerializer(journals, many=True)
#     return Response(serializer.data)


# UPDATE JOURNAL (OLD WAY)
# ---------------------------------------------------------
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_journal(request, pk):
#     try:
#         # Ownership check happens here manually
#         journal = Journal.objects.get(id=pk, user=request.user)
#     except Journal.DoesNotExist:
#         return Response({"error": "Not found"}, status=404)
#
#     serializer = JournalSerializer(journal, data=request.data)
#
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#
#     return Response(serializer.errors)


# DELETE JOURNAL (OLD WAY)
# ---------------------------------------------------------
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_journal(request, pk):
#     try:
#         journal = Journal.objects.get(id=pk, user=request.user)
#     except Journal.DoesNotExist:
#         return Response({"error": "Not found"}, status=404)
#
#     journal.delete()
#     return Response({"message": "Deleted successfully"})



# =========================================================
# NEW MODERN APPROACH (VIEWSET - ACTIVE CODE)
# =========================================================

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from journals.models import Journal
from journals.serializers import JournalSerializer
from rest_framework import filters

class JournalViewSet(ModelViewSet):
    """
    =====================================================
    JOURNAL VIEWSET (MODERN APPROACH)
    =====================================================

    This class replaces all old CRUD function-based views.

    WHAT IT HANDLES AUTOMATICALLY:
    -----------------------------------------------------
    GET    /journals/        -> list journals
    POST   /journals/        -> create journal
    GET    /journals/id/     -> retrieve single journal
    PUT    /journals/id/     -> update journal
    DELETE /journals/id/     -> delete journal

    SECURITY MODEL:
    -----------------------------------------------------
    - Only authenticated users can access
    - Each user only sees their own journals
    - Ownership is enforced via queryset filtering

    WHY THIS IS BETTER:
    -----------------------------------------------------
    - Less code
    - Cleaner structure
    - Easier maintenance
    - Production standard (industry practice)
    """

    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter,filters.OrderingFilter] #request level fitering? user preferance filter
    search_fields = ['title','content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        Return only journals belonging to logged-in user.
        This ensures data isolation between users.
        """
        return Journal.objects.filter(user=self.request.user).order_by('-created_at')#database/security  level filtering

    def perform_create(self, serializer):
        """
        Automatically assign journal ownership to logged-in user.
        Prevents frontend from manipulating user field.
        """
        serializer.save(user=self.request.user)


