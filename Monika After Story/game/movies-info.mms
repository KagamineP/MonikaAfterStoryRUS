
# Every line containing the character '#' will be discarded
# use them for commentary

## THIS TEXT HAS A SPECIAL SYNTAX, IT'S NOT A PYTHON ARCHIVE ##
## Every movie must start with the keyword "movie" followed by the name
## [DESCRIPTION]
## if "description" is the first word, the line will be used for Monika's description
## of the film
## The line MUST contain an image for her to display

## example:
## description 1o "This film talks about AI"
## description 1o "It could be fun"


## [MOVIE REACTIONS]
## if "m" is the first word, the line will be used for Monika's reactions.
## The line can or can not contain a reaction from the cheatsheet (like 1b)
## The line must contain the exact second where that reaction will be reproduced
## with the format [HH:MM:SS]
## The line must contain a message even if it's nothing, example: ""
## There must be a gap between lines of 10 seconds. The line will be automatically
## hide waiting for the next reaction

## example:
## m 1k [00:32:52] "Я терпеть не могу эти прыжки!"
## m [00:33:05] "Но они также забавны"
## m 4f [01:12:05] ""

## [CLOSURE]
## if "closure" is the first word, the line will be used for Monika's closure
## after the word closure add the event label which we'll push once the movie
## ends

## example:
## closure monika_difficulty

movie Doki Doki Trailer
description 3b "Так это трейлер к игре, да?"
description 1j "Давай посмотрим его вместе тогда, [player]!"
m 1lksdla [00:00:04] "Интересно, почему они поставили там предупреждение."
m 1hub [00:00:20] "А-ха-ха, я помню те стихи, которые ты пытался сделать."
m 1dsd [00:00:35] "Если бы они только меня представили, а не остальных..."
# TODO replace with an actual label for it
closure monika_difficulty