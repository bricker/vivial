from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice



class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question: Question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"]) # type: ignore
    except (KeyError, Choice.DoesNotExist):
        # back to vote form
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didnt select a choice!",
            },
        )
    else:
        # update the db, incrementing "votes" count
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # redirect after dealing w/ post data. Prevents double post if a user hits back button
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,))) # type: ignore
