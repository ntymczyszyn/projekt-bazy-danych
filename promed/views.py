from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the promed index.")


'''
Trzeba zrobić view
- do tworzenia konta?
- do logowana
- do odzyskiwania hasła
PACJENT
- do strony o pacjencie
- class do wyświetlania zarezerwowanych wizyt w terminarzu ? - do strony głównej u Patcjentów
- do przeglądania wizyt (wybór wizyty)
- do rezerwacji wizyty (nie wiem czy to nie będzie to samo co wyżej)
- do anulowania wizyty
- do przeglądania histoii wizyt
LEKARZ
- do strony o lekarzu
- do deklarowania dyspozycji
- do przeglądania wizyt ( to samo co u Pajcentów?, bo tam inne dane osoby będą, więc nie jestem pewna)
- do przeglądania historii wizyt
'''
def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')