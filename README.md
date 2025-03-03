# API Flask dla Aplikacji Mobilnej

API służące jako backend dla aplikacji mobilnej, obsługujące uwierzytelnianie użytkowników, zarządzanie wydarzeniami i przesyłanie plików. Wykorzystuje SQLite3 jako silnik bazy danych.

## Zależności

- **Flask**: Framework webowy dla API
- **Flask-Session**: Zarządzanie sesjami po stronie serwera
- **Flask-CORS**: Obsługa Cross-Origin Resource Sharing dla komunikacji między aplikacją Ionic a serwerem Flask
- **Flask-Mailman**: Funkcjonalność obsługi poczty email
- **CS50**: Wrapper (oprogramowanie pośredniczące) dla operacji na bazie danych SQL
- **Werkzeug**: Narzędzia do obsługi plików i haszowania haseł

## Zabezpieczenia

1. **Zarządzanie Sesjami**:
   - Przechowywanie sesji po stronie serwera w systemie plików
   - Włączone sesje permanentne
   - Bezpieczna konfiguracja sesji z flagami SameSite=None i Secure
   - Własny klucz tajny

2. **Bezpieczeństwo Haseł**:
   - Haszowanie haseł przy użyciu funkcji bezpieczeństwa Werkzeug
   - Funkcja resetowania hasła z kodami jednorazowymi
   - Weryfikacja email przy resetowaniu hasła

3. **Bezpieczeństwo Przesyłania Plików**:
   - Ograniczenie typów plików (tylko PNG, JPG, JPEG)
   - Limit rozmiaru pliku (5MB)
   - Bezpieczna obsługa nazw plików
   - Generowanie unikalnych nazw plików z timestampami
   - Czyszczenie starych plików przy aktualizacji avatara

4. **Uwierzytelnianie**:
   - Dekorator wymagający logowania dla chronionych endpointów
   - Uwierzytelnianie oparte na sesjach
   - Automatyczne czyszczenie sesji przy wylogowaniu

5. **Bezpieczeństwo Bazy Danych**:
   - Prepared statements dla zapytań SQL zapobiega SQL injection
   - Wymuszenie unikalności adresów email
   - Weryfikacja użytkownika przed modyfikacją danych

## Endpointy API

### Uwierzytelnianie

#### POST `/rejestracja`
- **Wejście**: JSON z `nazwa`, `haslo`, `email`
- **Odpowiedź**: Komunikat sukcesu lub błędu (duplikat nazwy/emaila)

#### POST `/logowanie`
- **Wejście**: JSON z `nazwa`, `haslo`
- **Odpowiedź**: Utworzenie sesji z danymi użytkownika

#### GET `/sesja-status`
- **Odpowiedź**: Informacje o aktualnej sesji

#### GET/POST `/wylogowanie`
- **Odpowiedź**: Czyszczenie sesji i usunięcie ciasteczka

### Reset Hasła

#### POST `/wyslij-kod`
- **Wejście**: JSON z `email`
- **Odpowiedź**: Wysyła 6-cyfrowy kod przez email

#### POST `/zmiana-hasla`
- **Wejście**: JSON z `email`, `noweHaslo`, `kodRes`
- **Odpowiedź**: Potwierdzenie aktualizacji hasła

### Zarządzanie Avatarem

#### POST `/dodaj-avatar`
- **Wejście**: Formularz multipart z plikiem avatara i ID użytkownika
- **Odpowiedź**: Potwierdzenie przesłania i aktualizacja ścieżki

### Zarządzanie Wydarzeniami

#### POST `/zapisz-wydarzenie`
- **Wejście**: JSON z szczegółami wydarzenia (nazwa, data, czas, miejsce, sloty, opis, gry)
- **Odpowiedź**: Potwierdzenie utworzenia

#### GET `/wydarzenia`
- **Odpowiedź**: Lista wszystkich wydarzeń ze szczegółowymi informacjami. Gry, które się przedawniły są odrzucane a reszta jest sortowana chronologicznie od najpóźniejszcyh.

#### POST `/zapisz-do-gry`
- **Wejście**: JSON z ID wydarzenia i preferencją gry
- **Odpowiedź**: Potwierdzenie rejestracji

#### POST `/usun-mnie-z-gry`
- **Wejście**: JSON z ID wydarzenia
- **Odpowiedź**: Potwierdzenie usunięcia

#### POST `/usun-wydarzenie`
- **Wejście**: JSON z ID wydarzenia
- **Odpowiedź**: Potwierdzenie usunięcia (tylko dla organizatora)

#### POST/PUT `/modyfikuj-wydarzenie`
- **Wejście**: JSON z ID wydarzenia i polami do aktualizacji
- **Odpowiedź**: Potwierdzenie modyfikacji

### Wyszukiwanie Gier

#### GET/POST `/gry`
- **Wejście**: Parametr zapytania lub JSON z tytułem gry
- **Odpowiedź**: Lista pasujących gier

### Lista ulubionych gier

#### POST `/dodaj-do-ulubionych`
- **Wejście**: JSON z nazwą gry
- **Odpowiedź**: Potwierdzenie dodania do ulubionych

#### POST `/usun-z-ulubionych`
- **Wejście**: JSON z nazwą gry
- **Odpowiedź**: Potwierdzenie usunięcia z ulubionych

## Formaty Danych

### Format Żądań
Wszystkie żądania powinny używać formatu JSON (z wyjątkiem przesyłania plików):
```json
{
    "nazwa": "nazwa_użytkownika",
    "haslo": "hasło",
    "email": "uzytkownik@przykład.pl"
}
```

### Format Odpowiedzi
Wszystkie odpowiedzi są w formacie JSON:
```json
{
    "komunikat": "Komunikat sukcesu"
}
```
lub dla błędów:
```json
{
    "blad": "Komunikat błędu"
}
```

## Obsługa Błędów
- Wszystkie endpointy zawierają bloki try-catch
- Szczegółowe komunikaty błędów
- Odpowiednie kody statusu HTTP (200, 400, 401, 404, 500)

## Kontrola Cache
Zapobiega zapisywaniu i buforowaniu odpowiedzi przez przeglądarki i serwery pośredniczące. Jest to ważne przy dynamicznych danych, jak status sesji czy lista wydarzeń
API implementuje nagłówki no-cache dla wszystkich odpowiedzi:
- Cache-Control: no-cache, no-store, must-revalidate
- Expires: 0
- Pragma: no-cache
