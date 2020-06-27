import json

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect  # noqa: 401
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic, View

from .diagnosisProcess import Choice, Question, DiagnoseProcess


class InitialView(View):
    template_name = 'polls/initial.html'
    context_object_name = 'latest_question_list'

    def get(self, request):
        return render(request, self.template_name,
                      {'symptom_list': json.dumps(list(DiagnoseProcess.weight_matrix.columns))})

    @staticmethod
    def post(request):
        selected = request.POST.get('selected', '')
        request.session['asked'] = [selected]
        request.session['positive'] = [selected]
        return redirect(reverse('polls:index'))


class QuestionView(View):
    template_name = 'polls/index.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dp = DiagnoseProcess()

    def get(self, request):
        asked = request.session.get('asked')
        positive = request.session.get('positive')
        self.dp.asked = asked
        self.dp.positive = positive
        self.dp.reduce()

        if self.dp.time_to_conclude():
            diagnosis = self.dp.check()
            request.session['diagnosis'] = diagnosis
            request.session.flush()
            messages.add_message(request, messages.INFO, 'Here is your diagnosis')
            return render(request, 'polls/conclude.html', {'diagnosis': dict(diagnosis)})

        symptom = self.dp.next_symptom()
        question = Question(
            question_text='Are you suffering from ' + str(symptom) + '? If yes, how severe is it?')
        return render(request, self.template_name, {'question': question})

    def post(self, request):
        asked = request.session.get('asked')
        positive = request.session.get('positive')
        self.dp.asked = asked
        self.dp.positive = positive
        self.dp.reduce()
        symptom = self.dp.next_symptom()

        choice = request.POST.get('choice', '')
        request.session['asked'].append(symptom)
        if choice in ['Severe', 'Moderate', 'light']:
            request.session['positive'].append(symptom)
        request.session.save()
        return redirect(reverse('polls:index'))


def restart(request):
    request.session.flush()
    messages.add_message(request, messages.INFO, 'Here we go again! 🚀')
    return redirect(reverse('polls:initial'))


def about(request):
    template_name = 'polls/about.html'
    return render(request, template_name)
