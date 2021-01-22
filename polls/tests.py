import datetime
from django.http import response
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text, votes):
    return Choice.objects.create(question=question, choice_text=choice_text, votes=votes)

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        # There should be at least one question.
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        # Past questions should show up
        q = create_question(question_text="Past question.", days=-30)
        create_choice(question=q, choice_text="choice", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question.>'])

    def test_future_question(self):
        # Future questions shouldn't
        q = create_question(question_text="Future question.", days=30)
        create_choice(question=q, choice_text="choice", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_future_question_and_past_question(self):
        p = create_question(question_text="Past question.", days=-30)
        f = create_question(question_text="Future question.", days=30)
        create_choice(question=p, choice_text="choice1", votes=0)
        create_choice(question=f, choice_text="choice2", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], 
                                                 ['<Question: Past question.>'])
    
    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        p1 = create_question(question_text="Past question 1.", days=-30)
        p2 = create_question(question_text="Past question 2.", days=-5)
        create_choice(question=p1, choice_text="choice1", votes=0)
        create_choice(question=p2, choice_text="choice2", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
    
    def test_questions_without_choices(self):
        """
        Tests that questions without choices aren't published.
        """
        create_question(question_text="New question wo choice", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        self.assertContains(response, "No polls are available.")

    def test_questions_with_choices(self):
        """
        Tests that questions with at least one choice are published.
        """
        cq = create_question(question_text="New question w choice", days=-2)
        create_choice(question=cq, choice_text="Whatever", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: New question w choice>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        create_choice(question=future_question, choice_text="choice", votes=0)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        create_choice(question=past_question, choice_text="choice", votes=0)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
    def test_question_no_choices(self):
        """
        The detail view of a question without choices returns 404
        """
        nc = create_question(question_text="no choices", days=-3)
        url = reverse('polls:detail', args=(nc.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_w_choices(self):
        """
        The detail view of a question with choices displays the question's text.
        """
        wc = create_question(question_text="w choices", days=-3)
        create_choice(question=wc, choice_text="choice", votes=0)
        url = reverse('polls:detail', args=(wc.id,))
        response = self.client.get(url)
        self.assertContains(response, wc.question_text)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        create_choice(question=future_question, choice_text="choice", votes=0)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        create_choice(question=past_question, choice_text="choice", votes=0)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
    def test_question_no_choices(self):
        """
        The results view of a question without choices returns 404
        """
        nc = create_question(question_text="no choices", days=-3)
        url = reverse('polls:results', args=(nc.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_w_choices(self):
        """
        The results view of a question with choices displays the question's text.
        """
        wc = create_question(question_text="w choices", days=-3)
        create_choice(question=wc, choice_text="choice", votes=0)
        url = reverse('polls:results', args=(wc.id,))
        response = self.client.get(url)
        self.assertContains(response, wc.question_text)
