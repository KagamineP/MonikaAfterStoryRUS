# Watch a movie module
#

label mas_monikamovie:
    init python:

        # pane constants
        MOVIE_X = 680
        MOVIE_Y = 40
        MOVIE_W = 560
        MOVIE_H = 640
        MOVIE_XALIGN = -0.05
        MOVIE_AREA = (MOVIE_X, MOVIE_Y, MOVIE_W, MOVIE_H)
        MOVIE_RETURN = "Я передумал[mas_gender_none]."


        gamedir = os.path.normpath(config.gamedir)

        ## CLASS DEFINITIONS ##
        #This class holds all the information relative to
        # Monika's dialogue and reactios of the film
        class AvaiableMovies:
            def __init__(self):
                self.listOfMovies = []
                self.checkMovies()

            def checkMovies(self):
                with open(os.path.join(gamedir, "movies-info.mms"),"r") as f: #duplicated code
                    lines = f.readlines()
                listOfStrings = [x.strip() for x in lines]

                #Now we parse the info
                for line in listOfStrings:
                    if "#" in line:
                        continue
                    partialSplittedSentence = line.split(" ", 1)
                    firstWord = ""
                    if len(partialSplittedSentence) >= 2:
                        firstWord = partialSplittedSentence[0]
                        data = partialSplittedSentence[1]
                    if "movie" in firstWord:
                        self.listOfMovies.append((data, data, False, False))

            def searchMovies(self, movieName):
                foundMovies = []
                for xName in self.listOfMovies:
                    if movieName.lower() in xName.lower():
                        foundMovies.append(xName)
                return foundMovies

        class ParsedMovie:
            def __init__(self, movieName):
                self.descriptionList = []
                self.reactionList = []
                self.closure = None
                self.currentReactionIndex = 0 #So monika can react again if user goes backwards
                self.retrieveMovie(movieName)

            def reactionsAreFinished(self):
                return self.currentReactionIndex >= len(self.reactionList)

            def stringReactionToTuple(self, string):
                emotion = None
                when = ""
                what = ""
                listOfInfo = []
                if not string[0] == "[": #with emotion
                    listOfInfo = string.split(" ", 2)
                    emotion = listOfInfo [0]
                    when = listOfInfo [1]
                    what = listOfInfo [2]
                else:
                    listOfInfo = string.split(" ", 1)
                    when = listOfInfo [0]
                    what = listOfInfo [1]
                return emotion,when,what

            def formattedTimeToSeconds(self, string):
                string = string.replace('[','')
                string = string.replace(']','')
                infoList = string.split(":")
                hours = int(infoList[0])
                minutes = int(infoList[1])
                seconds = int(infoList[2])
                return 3600*hours + 60*minutes + seconds

            def obtainCurrentReactionTuple(self):
                string = self.reactionList[self.currentReactionIndex]
                emotion, when, what = self.stringReactionToTuple(string)
                return emotion,when,what

            def popReaction(self):
                emotion, when, what = self.obtainCurrentReactionTuple()
                self.currentReactionIndex += 1
                return emotion,when,what


            def canReact(self, time):
                if(self.reactionsAreFinished()):
                    return False
                emotion, when, what = self.obtainCurrentReactionTuple()

                expectedToReact = self.formattedTimeToSeconds(when)
                return time > expectedToReact


            def popDescription(self):
                string = self.descriptionList.pop(0)
                stringArray = string.split(" ", 1)
                emotion = stringArray[0]
                line = stringArray[1]

                return emotion, line

            def hasDescription(self):
                return len(self.descriptionList) > 0

            def formatData(self, data):
                return data.replace('"','')

            def retrieveMovie(self, movieName):
                with open(os.path.join(gamedir, "movies-info.mms"),"r") as f:
                    lines = f.readlines()
                listOfStrings = [x.strip() for x in lines]

                #Now we parse the info
                filmFound = False
                for line in listOfStrings:
                    if "#" in line:
                        continue
                    partialSplittedSentence = line.split(" ", 1)
                    firstWord = ""
                    if len(partialSplittedSentence) >= 2:
                        firstWord = partialSplittedSentence[0]
                        data = partialSplittedSentence[1]
                        data = self.formatData(data)
                    if "movie" in firstWord:
                        filmFound = movieName == partialSplittedSentence[1]
                    if filmFound:
                        if "description" == firstWord:
                            self.descriptionList.append(data)
                        if "m" == firstWord:
                            self.reactionList.append(data)
                        if "closure" == firstWord:
                            self.closure = data

            def resynchronizeIndex(self, timer):
                self.currentReactionIndex = 0
                while((not (self.reactionsAreFinished())) and self.canReact(timer.seconds)):
                    self.currentReactionIndex += 1


        class MovieTimer:
            def __init__(self):
                self.seconds = 0
            def seconds(self):
                return self.seconds
            def addSeconds(self, secondsAdded):
                self.seconds += secondsAdded
            def formattedTime(self):
                secondsPool = self.seconds
                hours = int(secondsPool / 3600)
                secondsPool -= hours * 3600
                minutes = int(secondsPool / 60)
                secondsPool -= minutes * 60
                secs = secondsPool
                return hours, minutes, secs
            def setFormattedTime(self,hours,minutes,seconds):
                self.seconds = int(hours)*3600 + int(minutes)*60 + int(seconds)


        ## FUNCTION DEFINITIONS ##
        def iterate_timer(st, at, timer):
            #Time calculations
            deltaTime = st - globals()['lastCountdownTime']
            globals()['lastCountdownTime'] = st
            if watchingMovie:
                timer.addSeconds(deltaTime)

            #Render
            hours, minutes, secs = timer.formattedTime()
            d = Text("%02d:%02d:%02d" % (hours, minutes, secs))
            return d, 0.1
        def fastforward(timer,secondsAdded):
            timer.addSeconds(secondsAdded)

        def updateEmotionMonika(emotion):
            if emotion is not None:
                monika_reaction = "monika %s" % (emotion)
                renpy.show(monika_reaction)


        ## VARIABLES USED IN THIS MODULE ##
        watchingMovie = False
        lastCountdownTime = 0 #Used as global variable, use with caution
        firstComment = False
        timer = MovieTimer()
    # final quit item
    $ final_item = (MOVIE_RETURN, False, False, False, 20)

    $ listMovies = AvaiableMovies()

    m 1eub "Хочешь посмотреть кино?"

    label mm_choose_movie:

        m "Какой фильм вы хотели бы посмотреть?"

        # move Monika to the left
        show monika at t21

        # call scrollable pane
        call screen mas_gen_scrollable_menu(listMovies.listOfMovies, MOVIE_AREA, MOVIE_XALIGN, final_item)

        # move her back to center
        show monika at t11

        # return value? then push
        if _return:
            $ movieInformation = ParsedMovie(_return)
            jump mm_found_movie
        else:
            jump mm_movie_loop_end

    label mm_found_movie:
        $ MovieOverlayShowButtons()
        stop music fadeout 2.0
        image countdown = DynamicDisplayable(iterate_timer, timer)
        show countdown at topleft
        #Starts description Block
        python:
            while(movieInformation.hasDescription()):
                emotion, what =  movieInformation.popDescription()
                updateEmotionMonika(emotion)
                renpy.say(eval("m"), what)
        m 3eub "Давай синхронизируем начало фильма."
        m 1hub "Приготовься к началу фильма, Я сделаю обратный отсчет!"

        menu:
            "Готов[mas_gender_none]?"
            "Да.":
                label mm_movie_resume:
                    $ mas_RaiseShield_dlg()
                    m 1eua "Три...{w=1}{nw}"
                    m  "Два...{w=1}{nw}"
                    m  "Один...{w=1}{nw}"
                    # Movie loop
                    $ watchingMovie = True
                    label movie_loop:
                        pause 1.0
                        python:
                            if movieInformation.canReact(timer.seconds):
                                emotion, when, what = movieInformation.popReaction()
                                updateEmotionMonika(emotion)

                                if not (what == "" or what is None):
                                    what += "{w=10}{nw}"
                                    renpy.say(eval("m"), what)

                        if movieInformation.reactionsAreFinished():
                            hide countdown
                            $ MovieOverlayHideButtons()
                            m 1eua "Только что закончилось для меня! Тебе понравилось?"
                            jump mm_movie_closure

                        jump movie_loop

            "Нет.":
                hide countdown # Dupicated code, call function?
                $ MovieOverlayHideButtons()
                m 1eua "О, хорошо! Тогда я просто подожду тебя~"
                jump mm_movie_loop_end

        label mm_movie_closure:
            #Starts closure Block
            python:
                if movieInformation.closure:
                    pushEvent(movieInformation.closure)



    label mm_movie_loop_end:
        hide countdown
        $ mas_DropShield_dlg()
        $ watchingMovie = False
        $ timer.seconds = 0
        $ MovieOverlayHideButtons()
        $ play_song(store.songs.selected_track)
        show monika 1
        jump ch30_loop

    label mm_movie_pausefilm:
        $ watchingMovie = False
        m 1eub "О, ты только что поставил[mas_gender_none] фильм на паузу, [player]."
        menu:
            "Хочешь продолжить?"
            "Да.":
                m 1hua "Хорошо, [player]."
                jump mm_movie_resume
            "Нет.":
                m 1eua "О, тогда ладно, [player]."
                jump mm_movie_loop_end

    label mm_movie_settime:
        $ watchingMovie = False
        m 1eub "Ты хочешь синхронизировать время?"
        label mm_movie_repeattime:
            m 1eub "Скажи мне в формате ЧЧ:ММ:СС, [player]."
            python:
                player_dialogue = renpy.input('На какое время я должна установить фильм? ',default='',pixel_width=720,length=50)
                splittedTime = player_dialogue.split(":",2)
                bad_format = len(splittedTime) != 3
                if not bad_format:
                    hours = splittedTime[0]
                    minutes = splittedTime[1]
                    seconds = splittedTime[2]
                    bad_format = not (hours.isdigit() and minutes.isdigit() and seconds.isdigit())
                    if not bad_format:
                        bad_format = int(minutes) >= 60 or int(seconds) >= 60
            if bad_format:
                m 1lksdlc "Э..."
                m 1lksdlb "Извини, я не могу этого понять, [player]."
                m 1eka "Не забудь установить его в формате HH:MM:SS."
                m 3eua "Это «Часы:Минуты:Секунды.»"
                m "Вот пример для тебя, [player]."
                m "01:05:32"
                m 1eub "Это 1 час, 5 минут и 32 секунды."
                m 3hua "Так что попробуй еще раз!"
                jump mm_movie_repeattime
            else:
                $ timer.setFormattedTime(splittedTime[0],splittedTime[1],splittedTime[2])
                $ movieInformation.resynchronizeIndex(timer)
        m 1eua "Готово! Давай продолжим смотреть его!"
        jump mm_movie_resume
