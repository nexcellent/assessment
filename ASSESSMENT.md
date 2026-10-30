# Nexcent Coding Assessment – Aufgabenstellung

## Kontext

Für dieses Assessment arbeitest du an einem kleinen Ausschnitt von „Cendeo“. Cendeo ist eine Produktidee von uns, die wir bereits intern als Tool für die Verwaltung und Optimierung unserer Beraterprofile sowie das perfekt zugeschnittene Bewerben auf Projektausschreibungen verwenden.

Der Ausschnitt ist das Beraterprofil in einer etwas abgespeckten Variante, als eigenes öffentliches Repo auf GitHub, gleicher Stack und gleiche Konventionen wie im Produkt.

## Ausgangszustand

- Ein Beraterprofil besteht aus Stammdaten, beruflichen Stationen, Ausbildung, Skills mit Level und Referenzprojekten mit Zeitraum und eingesetzten Technologien.
- Das Repo hat die bei Nexcent übliche Projektstruktur: eine README, den Source Code in der entsprechenden Struktur, Tests, Fixtures und ein docker-compose.
- Fünf erfundene Beispielprofile unterschiedlicher Qualität liegen als Fixtures bei.

## Aufgabe

**Bau einen Qualitätscheck für das Beraterprofil.** Der Check soll zeigen, wie gut ein Profil ist, bevor es an einen Kunden geht, und was ein Nutzer daran verbessern kann. Was gut heißt, definierst du, genauso wie du prüfst, wie das Ergebnis aussieht und wie es in die Oberfläche kommt. Die fünf Beispielprofile sind unterschiedlich gut, daran kannst du dich orientieren. Erklär uns im Termin, warum du dich so entschieden hast und was ein Nutzer davon hat.

## Technische Vorgaben

- Der Check verändert das Profil nicht selbst. Entscheidung und Hoheit über das Profil liegen immer beim Nutzer.
- Das Projekt muss auf einem fremden Rechner mit den üblichen Entwicklertools laufen (macOS, VS Code, git, Docker). `docker compose up` startet es, und die Checks aus der README laufen grün durch.
- Falls du eine KI-API einsetzt, muss die App auch ohne Key starten und die Checks müssen ohne Internet laufen. Mock-Responses sind erlaubt. Erklär in der README, warum du KI an dieser Stelle einsetzt und wie du mit dem Non-Determinismus umgehst.
- Du darfst Libraries hinzufügen und die Struktur ändern, wenn du es begründest.
- Ein Deployment ist nicht nötig.

## Organisatorisches

- Bitte verbring nicht mehr als einen Abend mit der Aufgabe. Was fehlt, beschreibst du in der README.
- Fork am einfachsten unser Repo auf deinen GitHub-Account und arbeite dort, alles auf `main`. Die Abgabe ist der Link zu deinem öffentlichen Fork.
- Die README ist deine Doku und dein Entscheidungslog. Wir wollen darin ungefähr sehen, wie man das Projekt startet, was du gebaut hast und warum, was du bewusst weggelassen hast und was als Nächstes käme.
- KI-Coding-Tools darfst du gerne verwenden. Wir arbeiten intern selbst mit Claude Code und binden in unsere Produkte meist Claude- oder OpenAI-Modelle ein. Schreib kurz in die README, wie du sie eingesetzt hast.
- Wenn du eine KI-API einbindest, brauchst du einen eigenen API-Key oder arbeitest mit Mock-Responses.
- README und Termin können auf Deutsch oder Englisch sein, der Code bleibt Englisch.

## Bewertungskriterien

Wir schauen auf Herangehensweise, Produktdenken, Planung und Umsetzung, Codequalität, Architektur im Bestand und Weitblick. Im Termin solltest du Architektur, Grundideen, Aufbau und Paradigmen deiner Lösung erklären können.
