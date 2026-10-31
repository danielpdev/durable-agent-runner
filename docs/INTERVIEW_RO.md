# Pregătire pentru interviu — Durable Agent Runner

Roluri țintă: Agent Infrastructure / Backend.

## Prezentare de 90 de secunde

1. Explică problema concretă și cine folosește rezultatul.
2. Rulează `make demo` sau fluxul din UI.
3. Arată testul pentru un caz de eșec, apoi explică mecanismul din cod.
4. Spune ce limite are demonstrația și ce ai construi pentru producție.

Decizia de explicat: A job advances one durable step per transaction. The demonstrated business effect is stored in the same database transaction as its checkpoint, so a restart cannot duplicate that local effect.

## Cinci întrebări

1. Ce garantează checkpoint-ul?
2. Ce se întâmplă dacă procesul moare după efect?
3. De ce exact-once nu se extinde automat la HTTP?
4. Când poate anularea să oprească jobul?
5. Cum ai recupera un worker blocat?

## Exercițiu înainte de a aplica

Add worker leases, retry policy and a remote outbox adapter.

Alege o parte mică a acestei modificări, implementeaz-o personal, adaugă un test care verifică comportamentul și descrie rezultatul într-un commit real. Nu declara că ai înțeles sau construit singur o parte pe care nu o poți explica.

## Checklist personal

- [ ] Pot porni proiectul dintr-un checkout curat.
- [ ] Pot urmări cererea până la rezultatul salvat.
- [ ] Pot explica diferența dintre fixture și model local.
- [ ] Pot demonstra un eșec și recuperarea lui.
- [ ] Am făcut o modificare proprie și o pot explica în engleză.

Aceste puncte necesită review-ul tău; nu au fost bifate automat.
