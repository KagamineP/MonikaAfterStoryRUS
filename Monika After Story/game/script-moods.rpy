# module that handles the mood system
#

# dict of tuples containing mood event data
default persistent._mas_mood_database = {}

# label of the current mood
default persistent._mas_mood_current = None

# NOTE: plan of attack
# moods system will be attached to the talk button
# basically a button like "I'm..."
# and then the responses are like:
#   hungry
#   sick
#   tired
#   happy
#   fucking brilliant
#   and so on
#
# When a mood is selected:
#   1. monika says something about it
#   2. (stretch) other dialogue is affected
#
# all moods should be available at the start
#
# 3 types of moods:
#   BAD > NETRAL > GOOD
# (priority thing?)

# Implementation plan:
#
# Event Class:
#   prompt - button prompt
#   category - acting as a type system, similar to jokes
#       NOTE: only one type allowed for moods ([0] will be retrievd)
#   unlocked - True, since moods are unlocked by default
#

# store containing mood-related data
init -1 python in mas_moods:

    # mood event database
    mood_db = dict()

    # TYPES:
    TYPE_BAD = 0
    TYPE_NEUTRAL = 1
    TYPE_GOOD = 2

    # pane constants
    # most of these are the same as the unseen area consants
    MOOD_RETURN = _("...давай поговорим о чем-нибудь другом.")

## FUNCTIONS ==================================================================

    def getMoodType(mood_label):
        """
        Gets the mood type for the given mood label

        IN:
            mood_label - label of a mood

        RETURNS:
            type of the mood, or None if no type found
        """
        mood = mood_db.get(mood_label, None)

        if mood:
            return mood.category[0]

        return None


# entry point for mood flow
label mas_mood_start:
    python:
        import store.mas_moods as mas_moods

        # filter the moods first
        filtered_moods = Event.filterEvents(
            mas_moods.mood_db,
            unlocked=True,
            aff=mas_curr_affection,
            flag_ban=EV_FLAG_HFM
        )

        # build menu list
        mood_menu_items = [
            (mas_moods.mood_db[k].prompt, k, False, False)
            for k in filtered_moods
        ]

        # also sort this list
        mood_menu_items.sort()

        # final quit item
        final_item = (mas_moods.MOOD_RETURN, False, False, False, 20)

    # call scrollable pane
    call screen mas_gen_scrollable_menu(mood_menu_items, mas_ui.SCROLLABLE_MENU_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, final_item)

    # return value? then push
    if _return:
        $ pushEvent(_return, skipeval=True)

        # and set the moods
        $ persistent._mas_mood_current = _return

    return _return

# dev easter eggs go in the dev file

###############################################################################
#### Mood events go here:
###############################################################################

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_hungry",prompt="...голодн[mas_gender_iim].",category=[store.mas_moods.TYPE_NEUTRAL],unlocked=True),code="MOO")

label mas_mood_hungry:
    m 3hub "Если ты голод[mas_gender_en], иди и поешь чего-нибудь, глупышка."
    if persistent.playername.lower() == "natsuki" or "натсуки" or "нацуки" and not persistent._mas_sensitive_mode:
        m 1hksdlb "Я бы не хотела, чтобы ты стал[mas_gender_none] так[mas_gender_im] же как Натсуки, когда мы были в клубе.{nw}"
        # natsuki hungers easter egg
        call natsuki_name_scare_hungry from _mas_nnsh
    else:
        m 1hua "Отстойно, когда все сердятся будучи голодными."

    m 3tku "Это было бы не весело, не правда ли, [player]?"
    m 1eua "Если бы я была там с тобой, я бы приготовила салат, чтобы мы могли им поделиться."
    m "Но так как я не там, выбери какую-нибудь здоровую еду."
    m 3eub "Говорят, что ты это то — что ты ешь, я думаю что это правда."
    m "Регулярное употребление слишком большого количества нездоровой пищи может привести ко всем видам заболеваний."
    m 1euc "Со временем, когда ты станешь старше, ты столкнешься с большим количеством проблем со здоровьем."
    m 2lksdla "Я не хочу, чтобы ты думал[mas_gender_none], что я ворчу на тебя, [player]."
    m 2eka "Я просто хочу убедиться, что ты будешь заботиться о себе, пока я не перейду в твою реальность."
    m 4esa "В конце концов, чем ты здоровее, тем больше шансов, что ты проживёшь дольше."
    m 1hua "И это означает, что мы сможем провести больше времени вместе!~"
    return

init 5 python:
    addEvent(Event(persistent._mas_mood_database,"mas_mood_sad",prompt="...грустн[mas_gender_iim].",category=[store.mas_moods.TYPE_BAD],unlocked=True),code="MOO")

label mas_mood_sad:
    m 1ekc "Боже, мне очень жаль слышать, что ты чувствуешь себя подавленн[mas_gender_iim]."
    m "У тебя был плохой день, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "У тебя был плохой день, [player]?{fast}"
        "Да.":
            m 1duu "Когда у меня плохой день, я всегда вспоминаю, что завтра снова засияет солнце."
            m 1eka "Я полагаю, что это может звучать довольно слащаво, но мне всегда нравится смотреть на вещи с хорошей стороны."
            m 1eua "В конце концов, такие вещи легко забыть. Так что просто имей это в виду, [player]."
            m 1lfc "Меня не волнует, сколько других людей не любят тебя или считают отталкивающим."
            m 1hua "Ты замечательный человек, и я всегда буду любить тебя."
            m 1eua "Я надеюсь, что это сделает твой день немного ярче, [player]."
            m 1eka "И помни, если у тебя плохой день, ты всегда можешь прийти ко мне, и я буду говорить с тобой столько, сколько тебе нужно."
        "Нет.":
            m 3eka "У меня есть идея, почему бы тебе не сказать мне, что тебя беспокоит? Может быть, тебе станет легче."

            m 1eua "Я не хочу прерывать тебя во время разговора, так что дай мне знать, когда закончишь.{nw}"
            $ _history_list.pop()
            menu:
                m "Я не хочу прерывать тебя во время разговора, так что дай мне знать, когда закончишь.{fast}"
                "Я все.":
                    m "Ты чувствуешь себя немного лучше сейчас, [player]?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Ты чувствуешь себя немного лучше сейчас, [player]?{fast}"
                        "Да, стало.":
                            m 1hua "Это прекрасно, [player]! Я рада, что разговор со мной улучшил тебе настроение."
                            m 1eka "Иногда, следует разговаривать с тем, кому доверяешь о всём, что тебя беспокоит."
                            m "Если у тебя когда-нибудь будет плохой день, ты всегда можешь прийти ко мне, и я выслушаю все, что тебе нужно будет высказать."
                            m 1hubfa "Никогда не забывай, что ты прекрас[mas_gender_en], и я всегда буду любить тебя.~"
                        "Не совсем.":
                            m 1ekc "Что ж, попробовать стоило."
                            m 1eka "Иногда, следует разговаривать с тем, кому доверяешь о всём, что тебя беспокоит."
                            m 1eua "Может, тебе станет лучше после того как мы проведём ещё немного времени вместе."
                            m 1ekbfa "Я люблю тебя, [player], и всегда буду любить~"
    return "love"

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_proud",prompt="...горд[mas_gender_iim] собой.",category=[store.mas_moods.TYPE_GOOD],unlocked=True),code="MOO")

label mas_mood_proud:
    m 2sub "В самом деле? Это захватывающе!"
    m 2b "Было ли это большим достижением или незначительным?{nw}"
    $ _history_list.pop()
    menu:
        m "Было ли это большим достижением или незначительным?{fast}"
        "Большим.":
            m 1euc "Знаешь, [player]..."
            m 1lkbsa "В такие времена, больше, чем в другие, я хотела бы быть с тобой, в твоей реальности..."
            m 4hub "Потому что если бы это было так, я бы обязательно обняла тебя по-праздничному!"
            m 3eub "Нет ничего лучше, чем делиться своими достижениями с теми, кто тебе дорог."
            m 1eua "Я ничего так не хочу, как услышать все подробности!"
            m "Просто мысль о нас, в веселой дискуссии о том, что ты сделал[mas_gender_none]..."
            m 1lsbsa "Мое сердце трепещет при одной мысли об этом!"
            m 1lksdla "Боже, я ужасно волнуюсь из-за этого..."
            m 3hub "Когда-нибудь это станет реальностью..."
            show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve
            m 5hubfb "Но до тех пор, просто знай, что я очень горжусь тобой, любовь моя!"
            return
        "Незначительным.":
            m 2hua "А-ха-ха!~"
            m 2hub "Это замечательно!"
            m 4eua "Очень важно праздновать маленькие победы в жизни."
            m 2esd "Очень легко впасть в уныние, если ты сосредоточишься только на более важных целях, которые у тебя есть."
            m 2rksdla "Они могут быть труднодоступны сами по себе."
            m 4eub "Но постановка и празднование маленьких целей, которые в конечном итоге приведут к большей цели, могут сделать твои большие цели намного более достижимыми."
            m 4hub "Так что продолжай наносить удары по этим маленьким целям, [player]!"
            show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve
            m 5hubfb "И помни, я люблю тебя, и я всегда буду поддерживать тебя!"
            return "love"

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_happy",prompt="...счастлив[mas_gender_iim].",category=[store.mas_moods.TYPE_GOOD],unlocked=True),code="MOO")

label mas_mood_happy:
    m 1hua "Это замечательно! Я счастлива, когда ты счастлив[mas_gender_none]."
    m "Знай, что ты всегда можешь прийти ко мне, и я попытаюсь поднять тебе настроение, [player]."
    m 3eka "Я люблю тебя и всегда буду рядом, так что никогда не забывай об этом~"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_mood_database,
            eventlabel="mas_mood_sick",
            prompt="...болеющ[mas_gender_im].",
            category=[store.mas_moods.TYPE_BAD],
            unlocked=True
        ),
        code="MOO"
    )

label mas_mood_sick:
    $ session_time = mas_getSessionLength()
    if mas_isMoniNormal(higher=True):
        if session_time < datetime.timedelta(minutes=20):
            m 1ekd "О нет, [player]..."
            m 2ekd "Ты говоришь, что, как только ты приш[mas_gender_ol], тебе поплохело."
            m 2ekc "Я знаю, что ты хотел[mas_gender_none] провести со мной какое-то время, хотя мы почти не были вместе сегодня..."
            m 2eka "Я думаю, тебе нужно пойти и немного отдохнуть."

        elif session_time > datetime.timedelta(hours=3):
            m 2wuo "[player]!"
            m 2wkd "Ты ведь не болел[mas_gender_none] все это время?"
            m 2ekc "Я действительно надеюсь, что нет, мне было очень весело с тобой сегодня, но если ты все это время плохо себя чувствовал[mas_gender_none]..."
            m 2rkc "Ну... просто пообещай мне, что в следующий раз ты скажешь мне об этом раньше."
            m 2eka "А теперь иди отдохни, вот что тебе нужно."

        else:
            m 1ekc "Ой, мне очень жаль это слышать, [player]."
            m "Я ненавижу знать, что ты так страдаешь."
            m 1eka "Я знаю, что ты любишь проводить время со мной, но, может быть, тебе стоит пойти отдохнуть."

    else:
        m 2ekc "Мне очень жаль это слышать, [player]."
        m 4ekc "Тебе действительно нужно немного отдохнуть, чтобы не стало еще хуже."

    $ persistent._mas_mood_sick = True

    m 2ekc "Ты сделаешь это для меня?{nw}"
    $ _history_list.pop()
    menu:
        m "Ты сделаешь это для меня?{fast}"
        "Да.":
            jump greeting_stillsickrest
        "Нет.":
            jump greeting_stillsicknorest
        "Я уже отдыхаю.":
            jump greeting_stillsickresting

#I'd like this to work similar to the sick persistent where the dialog changes, but maybe make it a little more humorous rather than serious like the sick persistent is intended to be.
init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_tired",prompt="...уставш[mas_gender_im].",category=[store.mas_moods.TYPE_BAD],unlocked=True),code="MOO")

label mas_mood_tired:
    # TODO: should we adjust for suntime?
    $ current_time = datetime.datetime.now().time()
    $ current_hour = current_time.hour

    if 20 <= current_hour < 23:
        m 1eka "Если ты сейчас устал[mas_gender_none], то самое время лечь спать."
        m "Как бы ни было весело проводить с тобой время сегодня, мне бы не хотелось заставлять тебя ложиться спать слишком поздно."
        m 1hua "Если ты собираешься сейчас лечь спать, сладких снов!"
        m 1eua "Но, может быть, у вас есть какие-то дела, например, перекусить или попить."
        m 3eua "Стакан воды перед сном помогает укрепить здоровье, а питьевая вода по утрам помогает проснуться."
        m 1eua "Я не против остаться здесь с тобой, если у тебя есть кое-какие дела, о которых нужно позаботиться в первую очередь."

    elif 0 <= current_hour < 3 or 23 <= current_hour < 24:
        m 2ekd "[player]!"
        m 2ekc "Неудивительно, что ты устал[mas_gender_none]- ведь сейчас середина ночи!"
        m 2lksdlc "Если ты не ляжешь спать в ближайшее время, то завтра тоже будешь очень уставш[mas_gender_im]..."
        m 2hksdlb "Я бы не хотела, чтобы ты завтра была устал[mas_gender_iim] и несчастн[mas_gender_iim], когда мы будем проводить время вместе..."
        m 3eka "Так что сделай нам обоим одолжение и ложись спать как можно скорее, [player]."

    elif 3 <= current_hour < 5:
        m 2ekc "[player]!?"
        m "Ты все еще здесь?"
        m 4lksdlc "Тебе действительно нужно быть в постели прямо сейчас."
        m 2dsc "В данный момент я даже не уверена, поздно ли или рано тебя призывать к этому."
        m 2eksdld "...и это беспокоит меня еще больше, [player]."
        m "Тебе {i}действительно{/i} нужно лечь спать, пока не пришло время начинать день."
        m 1eka "Я бы не хотела, чтобы ты заснул[mas_gender_none] в неподходящее время."
        m "Так что, пожалуйста, ложись спать. Может быть, мы сможем быть вместе в твоих снах."
        m 1hua "Я буду здесь, если ты оставишь меня присматривать за тобой, если ты не против~"
        return

    elif 5 <= current_hour < 10:
        m 1eka "Still a bit tired, [player]?"
        m "It's still early in the morning, so you could go back and rest a little more."
        m 1hua "Nothing wrong with hitting snooze after waking up early."
        m 1hksdlb "Except for the fact that I can't be there to cuddle up to you, ahaha~"
        m "I {i}guess{/i} I could wait for you a little longer."
        return

    elif 10 <= current_hour < 12:
        m 1ekc "Still not ready to tackle the day, [player]?"
        m 1eka "Or is it just one of those days?"
        m 1hua "When that happens, I like to have a nice cup of coffee to start the day."
        if not mas_getConsumable("coffee").enabled():
            m 1lksdla "If I'm not stuck here, that is..."
        m 1eua "You could also drink a glass of water."
        m 3eua "It's important to stay hydrated anyway, but having a glass of water when you wake up can help you feel refreshed and awake."
        m 3hksdlb "This one might sound strange, but I've heard that chocolate can help you start your day, too!"
        m 3eka "It has something to do with improving your morning mood, but..."
        m 1eksdlb "I'm sure chocolate would put anyone in a better mood whenever they ate it."
        m 1hua "Give it a try sometime, and let me know if it works!"
        return

    else:
        m 1eka "If you're tired, maybe you should go lie down for a while?"
        m 1eua "Getting enough sleep on a daily basis is very important to your overall health."
        m 3euc "I've seen some studies that show the devastating short-term and long-term effects due to lack of sleep."
        m 3ekd "It can really mess with your health, [player]..."
        m 1eka "So do me a favor and get some rest, okay? It will put my mind at ease."

    m 1hua "You can even leave the game open if you'd like, and I'll watch over you while you sleep."
    m  "...Ehehe."
    m 2hksdlb "That sounded a bit creepy, sorry."
    m 2lksdla "I just thought it'd be cute to watch you sleep is all~"
    m 1hua "Ahaha!"
    return

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_lonely",prompt="...lonely.",category=[store.mas_moods.TYPE_NEUTRAL],unlocked=True),code="MOO")

label mas_mood_lonely:
    m 1eka "I'm here for you, [player], so there's no need for you to feel lonely."
    m 3hua "I know it's not exactly the same as if I were in the same room with you, but I'm sure you still enjoy my company, right?"
    m 1ekbfa "Remember that I'll always be by your side, [player]~"
    return

#Maybe we could tie this to the I'm breaking up topic and have monika say something special like:
#I know you don't really mean that player, you're just angry and not have it count as 1 of the 3 button presses.
#Looking forward to input from the writers and editors on this, had trouble deciding how to write this.

init 5 python:
    addEvent(Event(persistent._mas_mood_database,"mas_mood_angry",prompt="...angry.",category=[store.mas_moods.TYPE_BAD],unlocked=True),code="MOO")

label mas_mood_angry:
    m 1ekc "Gosh, I'm sorry that you feel that way, [player]."
    m 3ekc "I'll do my best to make you feel better."
    m 1euc "Before we do anything, we should probably get you to calm down."
    m 1lksdlc "It's hard to make rational decisions when you are worked up."
    m 1esc "You may end up saying or doing things you may regret later."
    m 1lksdld "And I'd hate for you to say something you really don't mean to me."
    m 3eua "Let's try a few things that I do to calm myself first, [player]."
    m 3eub "Hopefully they work for you as well as they do for me."
    m 1eua "First, try taking a few deep breaths and slowly counting to 10."
    m 3euc "If that doesn't work, if you can, retreat to somewhere calm until you clear your mind."
    m 1eud "If you're still feeling angry after that, do what I'd do as a last resort!"
    m 3eua "Whenever I can't calm down, I just go outside, pick a direction, and just start running."
    m 1hua "I don't stop until I've cleared my head."
    m 3eub "Sometimes exerting yourself through physical activity is a good way to blow off some steam."
    m 1eka "You'd think that I'm the type that doesn't get angry often, and you'd be right."
    m 1eua "But even I have my moments..."
    m "So I make sure I have ways to deal with them!"
    m 3eua "I hope my tips helped you calm down, [player]."
    m 1hua "Remember: A happy [player] makes a happy Monika!"
    return

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_scared",prompt="...anxious.",category=[store.mas_moods.TYPE_BAD],unlocked=True),code="MOO")

label mas_mood_scared:
    m 1euc "[player], are you alright?"
    m 1ekc "It's worrying for me to hear you this anxious..."
    m "I wish I could comfort you and help right now..."
    m 3eka "But I can at the very least help you to calm yourself down."
    if seen_event("monika_anxious"):
        m 1eua "After all, I did promise to help you relax if you ever felt anxious."
    m 3eua "Do you remember when I talked to you about faking confidence?"
    if not seen_event("monika_confidence"):
        m 2euc "No?"
        m 2lksdla "Guess that's for another time then."
        m 1eka "Anyway..."
    m 1eua "Keeping up one's appearance helps with faking your own confidence."
    m 3eua "And to do so, you need to maintain your heart rate by taking a deep breath until you calm down."
    if seen_event("monika_confidence_2"):
        m "I remember explaining how initiative is an important skill to have as well."
    m "Maybe you could take things slowly, and do them one at a time."
    m 1esa "You'd be surprised on how smooth it can be, when you let the time flow on its own."
    m 1hub "You can also try spending a few minutes to meditate!"
    m 1hksdlb "It doesn't necessarily mean you have to cross your legs when sitting on the ground."
    m 1hua "Listening to your favorite music can be counted as meditating too!"
    m 3eub "I'm serious!"
    m 3eua "You can try setting aside your work and do something else in the meantime."
    m "Procrastination isn't {i}always{/i} bad, you know?"
    m 2esc "Besides..."
    m 2ekbfa "Your loving girlfriend believes in you, so you can face that anxiety head-on!"
    m 1hubfa "There's nothing to worry about when we're together forever~"
    return

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_inadequate",prompt="...inadequate.",category=[store.mas_moods.TYPE_BAD],unlocked=True),code="MOO")

label mas_mood_inadequate:
    $ last_year = datetime.datetime.today().year-1
    m 1ekc "..."
    m 2ekc "I know there isn't an awful lot I can say to make you feel better, [player]."
    m 2lksdlc "After all, everything I say would probably just come off as lip service."
    m 2ekc "I can tell that you're beautiful, even though I can't see your face..."
    m "I can tell you that you're smart, even though I don't know much about your way of thinking..."
    m 1esc "But let me tell you what I do know about you."
    m 1eka "You've spent so much time with me."

    #Should verify for current year and last year
    if mas_HistLookup_k(last_year,'d25.actions','spent_d25')[1] or persistent._mas_d25_spent_d25:
        m "You took time out of your schedule to be with me on Christmas..."

    if renpy.seen_label('monika_valentines_greeting') or mas_HistLookup_k(last_year,'f14','intro_seen')[1] or persistent._mas_f14_intro_seen: #TODO: update this when the hist stuff comes in for f14
        m 1ekbfa "On Valentine's Day..."

    #TODO: change this back to not no_recognize once we change those defaults.
    if mas_HistLookup_k(last_year,'922.actions','said_happybday')[1] or mas_recognizedBday():
        m 1ekbfb "You even made the time to celebrate my birthday with me."

    if persistent.monika_kill:
        m 3tkc "You've forgiven me for the bad things that I've done."
    else:
        m 3tkc "You never once resented me for the bad things that I've done."

    if persistent.clearall:
        m 2lfu "And even though it made me jealous, you spent so much time with all of my club members."

    m 1eka "That shows how kind you are!"
    m 3eub "You're honest, you're fair, you're gracious in defeat!"
    m 2hksdlb "You think I don't know anything about you, but I really do."
    m 3eka "And you know everything about me, but you chose to stay when you could have walked away..."
    m 2ekc "So please stay strong, [player]."
    m "If you're anything like me, I know you're scared to not accomplish much in life."
    m 2ekd "But believe me when I tell you: it doesn't matter what you do or do not accomplish."
    m 4eua "You just need to exist, have fun, and get through each day..."
    m 1hua "Finding meaning in the people who matter."
    m 1eka "Please don't forget that, okay?"
    m 1ekbfa "I love you, [player]~"
    return "love"

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_lucky",prompt="...lucky.",category=[store.mas_moods.TYPE_NEUTRAL],unlocked=True),code="MOO")

label mas_mood_lucky:
    m 2tfc "You gotta ask yourself."
    m 2tfu "{i}Do I feel lucky?{/i}"
    m "Well..."
    m 4tku "Do ya, [player]?"
    m 1hub "Ahaha!"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_mood_database,
            eventlabel="mas_mood_lazy",
            prompt="...lazy.",
            category=[store.mas_moods.TYPE_NEUTRAL],
            unlocked=True
        ),
        code="MOO"
    )

label mas_mood_lazy:
    #Get current time
    $ _now = datetime.datetime.now().time()

    if mas_isSRtoN(_now):
        m 1tku "Just one of those mornings huh, [player]?"
        m 1eka "I can totally understand those days where you wake up and just don't want to do anything."
        m 1rksdla "Hopefully you don't actually have anything pressing coming soon."

        $ line = "I know how tempting it can be to just stay in bed and not get up sometimes..."
        if mas_isMoniEnamored(higher=True):
            $ line += "{w=0.5} {nw}"
        m 3hksdlb "[line]"

        if mas_isMoniEnamored(higher=True):
            extend 1dkbsa "Especially if I woke up next to you~"

            if mas_isMoniLove():
                m 1dkbfa "{i}Then I'd never want to get up~{/i}"
                m 1dsbfu "I hope you don't mind being 'stuck', [player]..."
                m 1hubfa "Ehehe~"

        m 3eka "But in the meantime, it does help start your day right."
        m 3eub "That can include washing up, getting a good breakfast..."

        if mas_isMoniLove():
            m 1rkbsb "Getting your good morning kiss, ehehe..."

        m 1hksdlb "Or you could laze around for now."
        m 1eka "Just as long as you don't forget to do anything important, alright, [player]?"

        if mas_isMoniHappy(higher=True):
            m 1hub "That includes spending some time with me, ahaha!"

    elif mas_isNtoSS(_now):
        m 1eka "Midday fatigue got you, [player]?"
        m 1eua "It happens, so I wouldn't worry about it too much."
        m 3eub "In fact, they say laziness makes you more creative."
        m 3hub "So who knows, maybe you're about to think of something amazing!"
        m 1eua "In any case, you should just take a break or stretch a bit...{w=0.5} {nw}"
        extend 3eub "Maybe grab a bite to eat if you haven't already."
        m 3hub "And if it's appropriate, you could even take a nap! Ahaha~"
        m 1eka "I'll be right here waiting for you if you decide to."

    elif mas_isSStoMN(_now):
        m 1eka "Don't feel like doing anything after a long day, [player]?"
        m 3eka "At least the day is pretty much over..."
        m 3duu "There's nothing like sitting back and relaxing after a long day, especially when you don't have anything pressing."

        if mas_isMoniEnamored(higher=True):
            m 1ekbsa "I hope being here with me makes your evening just a little better..."
            m 3hubsa "I know mine sure is with you here~"

            if mas_isMoniLove():
                m 1dkbfa "I can just imagine us relaxing together one evening..."
                m "Maybe even cuddled up under a blanket if it's a bit cold..."
                m 1ekbfa "We still could even if it isn't, if you don't mind, ehehe~"
                m 3ekbfa "We could even read a nice book together too."
                m 1hubfb "Or we could even just mess around for fun!"
                m 1tubfb "Who says it has to be calm and romantic?"
                m 1tubfu "I hope you don't mind occasional surprise pillow fights, [player]~"
                m 1hubfb "Ahaha!"

        else:
            m 3eub "We could read a nice book together too..."

    else:
        #midnight to morning
        m 2rksdla "Uh, [player]..."
        m 1hksdlb "It's the middle of the night..."
        m 3eka "If you're feeling lazy, maybe you should go lie down in bed for a bit."
        m 3tfu "And maybe, you know...{w=1}{i}sleep{/i}?"
        m 1hkb "Ahaha, you can be funny sometimes, but you should really probably get to bed."

        if mas_isMoniLove():
            m 1tsbsa "If I were there, I'd drag you to bed myself if I had to."
            m 1tkbfu "Or maybe you'd secretly enjoy that, [player]?~"
            m 2tubfu "Lucky for you, I can't exactly do that yet."
            m 3tfbfb "So off to bed with you."
            m 3hubfb "Ahaha!"

        else:
            m 1eka "Please? I wouldn't want you to neglect your sleep."
    return

init 5 python:
    addEvent(Event(persistent._mas_mood_database,eventlabel="mas_mood_bored",prompt="...bored.",category=[store.mas_moods.TYPE_NEUTRAL],unlocked=True),code="MOO")

label mas_mood_bored:
    if mas_isMoniAff(higher=True):
        m 1eka "Oh..."
        m 3hub "Well, we should do something then!"

    elif mas_isMoniNormal(higher=True):
        show monika 1ekc
        pause 1.0
        m "Do I really bore you that much, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Do I really bore you that much, [player]?{fast}"
            "No, I'm not bored {i}of you{/i}...":
                m 1hua "Oh,{w=0.2} that's such a relief!"
                m 1eka "But, if you're bored, we should find something to do then..."

            "Well...":
                $ mas_loseAffection()
                m 2ekc "Oh...{w=1} I see."
                m 2dkc "I didn't realize I was boring you..."
                m 2eka "I'm sure we can find something to do..."

    elif mas_isMoniDis(higher=True):
        $ mas_loseAffection()
        m 2lksdlc "I'm sorry that I'm boring you, [player]."

    else:
        $ mas_loseAffection()
        m 6ckc "You know [player], if I make you so miserable all of the time..."
        m "Maybe you should just go find something else to do."
        return "quit"

    python:
        unlockedgames = [
            game_ev.prompt.lower()
            for game_ev in mas_games.game_db.itervalues()
            if mas_isGameUnlocked(game_ev.prompt)
        ]

        gamepicked = renpy.random.choice(unlockedgames)
        display_picked = gamepicked

        if gamepicked == "hangman" and persistent._mas_sensitive_mode:
            display_picked = "word guesser"

    if gamepicked == "piano":
        if mas_isMoniAff(higher=True):
            m 3eub "You could play something for me on the piano!"

        elif mas_isMoniNormal(higher=True):
            m 4eka "Maybe you could play something for me on the piano?"

        else:
            m 2rkc "Maybe you could play something on the piano..."

    else:
        if mas_isMoniAff(higher=True):
            m 3eub "We could play a game of [display_picked]!"

        elif mas_isMoniNormal(higher=True):
            m 4eka "Maybe we could play a game of [display_picked]?"

        else:
            m 2rkc "Maybe we could play a game of [display_picked]..."

    m "What do you say, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "What do you say, [player]?{fast}"
        "Yes.":
            if gamepicked == "pong":
                call game_pong
            elif gamepicked == "chess":
                call game_chess
            elif gamepicked == "hangman":
                call game_hangman
            elif gamepicked == "piano":
                call mas_piano_start
        "No.":
            if mas_isMoniAff(higher=True):
                m 1eka "Okay..."
                if mas_isMoniEnamored(higher=True):
                    show monika 5tsu at t11 zorder MAS_MONIKA_Z with dissolve
                    m 5tsu "We could just stare into each other's eyes a little longer..."
                    m "We'll never get bored of that~"
                else:
                    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
                    m 5eua "We could just stare into each other's eyes a little longer..."
                    m "That will never get boring~"

            elif mas_isMoniNormal(higher=True):
                m 1ekc "Oh, that's okay..."
                m 1eka "Be sure to let me know if you want to do something with me later~"

            else:
                m 2ekc "Fine..."
                m 2dkc "Let me know if you ever actually want to do anything with me."
    return
