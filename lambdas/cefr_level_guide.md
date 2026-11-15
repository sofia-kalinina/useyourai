# CEFR level guide for exercise generation

How useyourai should pitch grammar exercises at each CEFR level, in any European language. Written for the exercise-generation prompt and for people reviewing its output.

The levels come from the Council of Europe's CEFR. The task types come from the official Cambridge and Goethe-Institut exam specifications. Wording here is our own summary, not a copy of either.

## How to use this guide

- **Levels describe the learner, not the language.** A1 means the same in German, Romanian or Finnish. Apply each level's limits to the target language's own grammar.
- **Grammar order differs between languages.** This guide gives principles, not one grammar list. Within each language, choose structures a learner at that level would reasonably have met, in the order that language is usually taught.
- **The requested topic sets the grammar point; the level sets everything else.** "German accusative at C1" still drills the accusative, but with C1 sentences, contexts and traps.
- **When the topic is normally taught above the level** (conditionals, past tenses or aspect at A1), the topic still wins over the level's limits. Keep it learnable: use fixed chunks, short sentences, a word bank or a named form, and keep the target contrast as the thing the learner chooses. Every other word stays at the level.

## Variety seed

Each request comes with a **variety seed** chosen at random by the app. It gives, for each item slot: a situation type, a person's name, an item shape, a format allowed at the level, a spark type, a sub-rule number and a trigger style. Follow it slot by slot.

- **Situation:** interpret it freely. "A lost-and-found desk" can be a dialogue, a notice or a story.
- **Name:** use it for the main person. Adapt the spelling to the target language if needed.
- **Item shape:** the kind of text the item is written as: dialogue line, notice or sign, text message, headline, diary line, list or instruction, story sentence, quote, email line, announcement.
- **Format:** the task format from the table below. If a format can't carry the topic naturally (word formation or register shift for a tense contrast, for example), swap it for another allowed format not yet used in the set, and say so in a note. Never bend the topic to fit a format.
- **Spark type:** the kind of twist the item builds on (see the spark pool). The twist must decide the answer.
- **Trigger style:** how the learner can tell which answer is right. *Named*: a time, frequency or other cue word in the sentence. *Implied*: the situation or a consequence makes it clear, with no cue word. *Contrast*: an earlier line in the item sets up the choice. At least 3 of 5 items in a set must be implied or contrast.
- **Sub-rule number:** after you list the sub-rules (see "Plan before writing"), use the sub-rule at that position for this item. If the number is larger than your list, count round again from the start. If no unused format is left for a swap, reuse the format used least so far and say so.
- If a seed situation can't carry the grammar point naturally, pick another from the same broad area, never a banned one.
- If no seed is given, choose situations, names, shapes and formats yourself, all different, avoiding the banned lists.

**Banned stock situations:** hotel or restaurant reviews, escaped or misbehaving animals in the news, grandparents as the default older person, landlord letters, works councils, ordering coffee, introducing yourself at a party, the weather as small talk.

**Banned overused props and twists:** umbrellas, pyjamas, socks, parrots, pianos; salt instead of sugar; the wrong parcel arriving; shooting an apple off a head; a child beating adults; "first time ever" or "finally after N years"; a power cut wiping out work; green hair at the hairdresser; burnt bread; a dentist banning sweets; twins as mistaken identity; an overheard "she" or "you" that turns out to be an object; typos in fine amounts; "X bets N euros that…"; cakes or pies as the default food; "read it but never finished".

## Plan before writing

1. **List the sub-rules, with their clichés.** Write down at least eight distinct sub-rules or triggers of the requested grammar point that suit the level: for example, for a two-tense contrast, background vs event, interrupted action, repeated past action, duration, result, description; for a case, each preposition group, verb government, time phrases, fixed expressions.
For each sub-rule, also write the textbook example sentence and cue word everyone uses for it (for perfective aspect: "already" plus a finished cake). Then avoid that sentence pattern and, unless the seed's trigger style is "named", that cue word.
2. **Assign one per item.** At most two items in a set may share a sub-rule or trigger.
3. **No shared sentence frame.** A frame is the gap position plus the predicate pattern. No two items in a request may share one, for example "[Name] gives [person] [thing]" twice, or "___ is [adjective]" twice.
4. **No repeated twist** across the sets of one request. A twist is its mechanism ("it was only once", "it turns out to be an object"), not only its prop.

## Rules for every level

1. **One clear correct answer per item, or a stated set of accepted answers.** For open items (open gap, translation, rewrite, register shift, "say why"), name the **key part** the checker must find, and list accepted alternatives.
2. **Try to break each item before returning it.** Answer every open item a second way. If the second answer is also correct, either accept it in the key or narrow the item until it isn't. Watch for time words that allow both past tenses, gaps where a possessive or a different article fits, word order variants, infinitive versus imperative after request verbs, and synonyms. When an instruction excludes an answer, exclude the whole structure ("don't use a relative clause"), not one word. For past-tense contrasts, test both readings (background and sequence) wherever a "when" clause or a past event sits nearby. If the twist is the speaker's own excuse or lie, put the gap in narration or accept both forms.
3. **Test the requested grammar point, nothing else.** Every other word should be easy for the level. If removing the target grammar leaves the item still hard, simplify the rest.
4. **Never give the answer away.** The exact answer word or phrase doesn't appear elsewhere in the item; other words in the same case, tense or form are fine. Instructions don't name the rule that decides the answer and don't supply the deciding word ("use the negative form" is a giveaway when negation triggers the case). Length limits ("one word", "three to five words") are fine for narrowing answers.
5. **Real language only.** Messages, notices, conversations, articles, stories, things people actually say or write. Never sentences built only to show a rule.
6. **At least 3 of every 5 items need a spark**, built on the seed's spark type. **Swap test:** replace the twist with a plain, neutral version of the same sentence. If the item is just as interesting, it isn't a spark. Of those 3, at least 2 must have a twist that decides the answer: with the plain version, the other option would be correct. The other 2 items may be plain. A colour, an odd object or a mild joke is not a spark. Dull but correct counts as a failure.
7. **Vary everything inside a set:** situation, person, item shape, format, and sub-rule (see the seed and the plan). Use at least 3 formats in a set of five, at least 4 from B1 up.
8. **Everything the learner sees outside the target-language content is in the interface language** (English or Ukrainian): instructions, labels, glosses, option letters' explanations. Fields only the checker sees (expected answer, key part, accepted alternatives) can be in any language. When the target language and interface language are the same, don't use translation; use another allowed format.
9. **Glossing is allowed** for one word per item that isn't part of the grammar point, in brackets in the interface language.
10. **No trick questions, no trivia.** Difficulty comes from the language, not obscure facts.
11. **Error correction must be safe.** The error must be wrong in every standard register, not just unusual.
12. **Sentence transformation must be closed.** The source sentence must mean exactly what the key says. List every other way to use the key word (another preposition, another case) and accept it or exclude it in the instruction.
13. **Real words only.** Every word must be a standard dictionary form. If unsure, rephrase with a word you are sure of.
14. **Short instructions:** at most about 35 words at A1–B1 and 50 at C1. Put the twist inside the target-language text where possible.
15. **Situations don't repeat** across the sets of one request.

## Task formats

This table is the single source of truth for which formats are allowed at which levels.

| Format | What the learner does | Levels |
|---|---|---|
| Gap fill with word bank | Choose the right form from 3–4 options | A1–B1 |
| Gap fill, open | Write one missing word or form | A2–C2 |
| Form transformation | Put a given word into the right form (case, tense, agreement). For two-form topics (aspect, ser or estar) give one base form, not the pair | A1–C1 |
| Choose between two forms | Pick one of two given options and write it correctly. Options can be two forms of one word (two tenses, two aspects, two cases, with or without the article), two verbs with different government, or two function words. Both options must make sense on their own; the context decides. No nonsense distractors | A1–C2 |
| Translation, short | Translate one sentence from the interface language | A1–B2 |
| Error correction | Find and fix one error in a sentence | A2–C2 |
| Sentence completion | Finish a sentence so it is correct and makes sense | A2–B2 |
| Sentence transformation | Rewrite a sentence with the same meaning, using a given key word | B1–C2 |
| Word formation | Build the right word from a stem (prefix, suffix, compound) | B2–C2 |
| Register shift | Rewrite a sentence for a different situation (formal, informal, written, spoken) | B2–C2 |
| Choose the nuance | Pick one of two or three options that are all grammatical on their own and in the sentence, where meaning or tone decides. Answer: the option, plus a reason of at most five words that names the meaning, for example "finished action", "ongoing background" | C1–C2 |
| Mini-dialogue | Complete one line of a two- or three-line exchange | A1–B2 |

## Level by level

### A1 — Beginner

- **Learner can:** use familiar everyday expressions; introduce themselves; ask and answer simple questions about people, places and things they own; follow slow, clear speech.
- **Sentences:** usually one clause, at most 10 words in the sentence with the gap or the sentence to translate. Very common words only: family, numbers, days, food, home, colours, basic jobs.
- **Grammar:** present tense of common verbs, basic word order, personal pronouns, articles or gender and simple plurals where the language has them, basic questions and negation. For cases or endings, the most frequent forms first.
- **Avoid:** idioms, rare words, long sentences.

### A2 — Elementary

- **Learner can:** handle routine exchanges on familiar matters; describe their background and surroundings simply.
- **Sentences:** one or two clauses joined by simple linkers (and, but, because). About 6–12 words.
- **Grammar:** common past form, simple future, comparatives, common prepositions, frequent irregular forms, possessives, modal verbs for ability and wishes.
- **Avoid:** abstract topics, long sentences, rare tenses.

### B1 — Intermediate

- **Learner can:** understand the main points of clear standard texts on familiar matters; describe experiences, plans and hopes, and give short reasons for opinions.
- **Sentences:** up to about 20 words, with one subordinate clause.
- **Grammar:** contrasts between past forms, common conditionals, relative clauses, the most common passive, modal verbs for advice and obligation, reported statements.
- **Avoid:** specialist vocabulary, literary style, rare idioms.

### B2 — Upper intermediate

- **Learner can:** understand the main ideas of complex texts on concrete and abstract topics; argue a view and weigh pros and cons.
- **Sentences:** several clauses, linkers of contrast and concession.
- **Grammar:** full range of tenses and aspect, less common conditionals, passive variants, verb patterns, common collocations and phrasal expressions.
- **Avoid:** archaic or highly regional language unless asked.

### C1 — Advanced

- **Learner can:** understand long, demanding texts and implied meaning; use the language flexibly for social, academic and work purposes.
- **Sentences:** long and well built, with control of emphasis, linking and reference.
- **Grammar:** fine distinctions between near-equivalent structures, emphasis through word order where the language has it, subjunctive or conditional nuance, participle and nominal style, collocations, fixed phrases, idiomatic verb patterns, word formation.
- **Make it C1, the cover test:** cover everything except the sentence the learner works on (the gap sentence, the sentence to correct or the sentence to rewrite). If one word there settles the answer by a rule taught at A1–B1, the item is B1–B2. At least 3 of 5 items must pass. The answer must itself be a form of the target grammar; fixed chunks and simple register changes (informal to formal "you") don't count. At most one item per set may rest on a B1 rule. If the topic has only one meaning contrast, use it at most twice.

### C2 — Proficient

- **Learner can:** understand almost everything; express shades of meaning precisely, even in complex situations.
- **Grammar:** rare but real structures, stylistic choices, idioms in context, precise near-synonyms, register mixing for effect.
- **Make it C2:** as C1, with finer distinctions, and with real writing styles: literary, legal, academic, speeches.

## Self-check before returning a set

- Does every item drill the requested grammar point, with every other word easy for the level?
- Did I try to break each open item, and is every correct answer accepted?
- Do instructions avoid naming the rule, and is the target form absent elsewhere in the item?
- Does each item use a different seed situation and name, with none from the banned list?
- Do at least 3 items have a spark?
- At C1 and C2, do at least 3 items pass the cover test?
- Did I follow the seed slot by slot, with a different sub-rule per item and no shared sentence frame?
- Did I avoid each sub-rule's textbook sentence, and are at least 3 items implied or contrast?
- Is every word a real dictionary form?

## Situation pool for the variety seed

For each request the app draws, without repeats: 5 situation types from this pool, 5 names from a list of common names for the target language, 5 item shapes, 5 formats from those allowed at the level, 5 spark types, 5 sub-rule numbers from 1–8, and 5 trigger styles (at least 3 implied or contrast). One of each goes to each item slot.

A lost-and-found desk · a group chat planning something · a delivery gone wrong · a museum audio guide · a neighbour's note on a door · a job interview · a sports match commentary · a recipe gone wrong · a train announcement · a birthday surprise · a first day at a new job · a podcast intro · a library late-fee notice · a plant-care instruction · a cooking class · a theatre rehearsal · a lost passport at an airport · a flat-share cleaning rota · a phone repair shop · a weather-ruined wedding · a city bike rental · a pharmacy counter · a parent-teacher meeting · a startup pitch · a volunteer beach clean-up · a ferry timetable · a karaoke night · a broken lift notice · a second-hand market · a mountain hut guestbook · a hairdresser appointment · a tax office letter · a dance class · a chess club · a fishing trip · an online course review · a court summons · a newspaper correction · a lecture on bees · a dentist's reminder · a ski lesson · a bakery's opening day · a power cut · a film festival queue · a translation agency email · a garden allotment dispute · a choir concert · a heritage walking tour · a coding bootcamp · a supermarket loyalty card · a medieval fair

## Spark pool

For each item the app draws a spark type, without repeats within a request: a misunderstanding · a reversal of expectation · a confession · a deadline about to pass · mistaken identity · a secret coming out · a compliment that is really a complaint · an excuse that gives itself away · a rule broken for a good reason · an overheard line out of context · a promise about to be broken · a plan that worked too well · two people remembering it differently · a small lie · good news delivered badly · a correction that makes things worse · an unexpected expert · a bet · a coincidence · a last-minute change

## Sources

- Council of Europe, [CEFR global scale, Table 1](https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale) and the [CEFR Companion Volume](https://rm.coe.int/16809ea0d4)
- Cambridge English, [B1 Preliminary for Schools handbook](https://www.cambridgeenglish.org/Images/168143-cambridge-english-preliminary-for-schools-teachers-handbook.pdf) and [C1 Advanced handbook](https://www.cambridgeenglish.org/Images/167804-c1-advanced-handbook.pdf)
- Goethe-Institut, [C1 test description](https://www.goethe.de/pro/relaunch/prf/el/Pruefungsziele_Testbeschreibung_C1.pdf) and [model tests](https://goethe.de/en/spr/prf/vor.html)
- Instituto Cervantes, [DELE exams](https://cervantes.org/es/examenes/dele), and France Éducation international, [DELF A1 sample tasks](https://www.france-education-international.fr/diplome/delf-tout-public/niveau-a1/exemples-sujets?langue=fr) (not read in detail)
