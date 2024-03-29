default persistent._mas_game_database = dict()

init -10 python in mas_games:
    import store

    #Runtime eventlabel: event map for game evs
    game_db = {}

    def is_platform_good_for_chess():
        import platform
        import sys

        if sys.maxsize > 2**32:
            return platform.system() == 'Windows' or platform.system() == 'Linux' or platform.system() == 'Darwin'

        else:
            return platform.system() == 'Windows'

init 1 python in mas_games:
    #Constant for hangman name
    #NOTE: This is adjusted in the mas_pick_a_game label
    HANGMAN_NAME = _("Висилица") if not store.persistent._mas_sensitive_mode else _("Угадай слово")

    def _total_games_played(exclude_list=[]):
        """
        Returns the total number of games played by adding up the shown_count of each game

        IN:
            exclude_list - A list of event_label strings for games we want to exclude from the number of games played
                defaults to an empty list
        """
        global game_db

        total_shown_count = 0
        for ev in game_db.itervalues():
            if ev.eventlabel not in exclude_list:
                total_shown_count += ev.shown_count

        return total_shown_count

init 7 python in mas_games:
    def getGameEVByPrompt(gamename):
        """
        Gets the game ev using the prompt of its event (gamename)

        IN:
            gamename - Name of the game we want to get

        OUT:
            event object for the game entered if found. None if not found
        """
        global game_db

        #Adjust the gamename to be lower prior to looping
        gamename = gamename.lower()

        #Now search
        for ev in game_db.itervalues():
            if renpy.substitute(ev.prompt).lower() == gamename:
                return ev
        return None

#START: Global functions for handling games
init 8 python:
    def mas_isGameUnlocked(gamename):
        """
        Checks if the given game is unlocked.

        IN:
            gamename - name of the game to check

        OUT:
            True if the game is unlocked, False if not, or the game doesn't exist
        """
        game_ev = mas_games.getGameEVByPrompt(gamename)

        if game_ev:
            return (
                game_ev.unlocked
                and (not game_ev.conditional or (game_ev.conditional and eval(game_ev.conditional)))
                and game_ev.checkAffection(store.mas_curr_affection)
            )
        return False

    def mas_unlockGame(gamename):
        """
        Unlocks the given game.

        IN:
            gamename - name of the game to unlock
        """
        game_ev = store.mas_games.getGameEVByPrompt(gamename)
        if game_ev:
            game_ev.unlocked = True

    def mas_lockGame(gamename):
        """
        Locks the given game.

        IN:
            gamename - name of the game to lock
        """
        game_ev = store.mas_games.getGameEVByPrompt(gamename)
        if game_ev:
            game_ev.unlocked = False

#Initialize our games
init 5 python:
    addEvent(
        Event(
            persistent._mas_game_database,
            eventlabel="mas_pong",
            prompt="Пинг-понг",
            unlocked=True
        ),
        code="GME",
        restartBlacklist=True
    )

label mas_pong:
    call game_pong
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_game_database,
            eventlabel="mas_chess",
            prompt="Шахматы",
            conditional=(
                "not renpy.seen_label('mas_chess_dlg_qf_lost_ofcn_6') "
                "and mas_games.is_platform_good_for_chess() "
                "and mas_timePastSince(persistent._mas_chess_timed_disable, datetime.timedelta(hours=1))"
            )
        ),
        code="GME",
        restartBlacklist=True
    )

label mas_chess:
    $ persistent._mas_chess_timed_disable = None
    call game_chess
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_game_database,
            eventlabel="mas_hangman",
            prompt="[mas_games.HANGMAN_NAME]"
        ),
        code="GME",
        restartBlacklist=True
    )

label mas_hangman:
    call game_hangman
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_game_database,
            eventlabel="mas_piano",
            prompt="Пианино"
        ),
        code="GME",
        restartBlacklist=True
    )

label mas_piano:
    call mas_piano_start
    return

label mas_pick_a_game:
    # we can assume that getting here means we didnt cut off monika
    $ mas_RaiseShield_dlg()

    python:
        #Adjust for this name
        mas_games.HANGMAN_NAME = _("Виселица") if not persistent._mas_sensitive_mode else _("Угадай слово")

        #Decide the say dialogue
        play_menu_dlg = store.mas_affection.play_quip()[1]

        #Now let's get all of the unlocked games at the aff level
        game_menuitems = sorted([
            (ev.prompt, ev.eventlabel, False, False)
            for ev in mas_games.game_db.itervalues()
            if mas_isGameUnlocked(renpy.substitute(ev.prompt))
        ], key=lambda x:renpy.substitute(x[0]))

        ret_back = ("Неважно.", False, False, False, 20)

    #Move Moni left
    show monika 1eua at t21

    #Say the game line
    $ renpy.say(m, play_menu_dlg, interact=False)

    #Call scrollable pane
    call screen mas_gen_scrollable_menu(game_menuitems, mas_ui.SCROLLABLE_MENU_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, ret_back)

    $ selected_game = _return

    if selected_game:
        show monika at t11
        $ pushEvent(selected_game, skipeval=True)

    if not renpy.showing("monika idle"):
        show monika idle at t11

    $ mas_DropShield_dlg()

    jump ch30_loop
