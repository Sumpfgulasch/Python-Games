import pygame, sys, copy
from pygame.locals import *

pygame.init()

# WICHTIGE VARIABLEN
res = (720,720)
framerate = 30
winCondition = 5 # = Anzahl der eig. Steine, die in gegn. Basis sein müssen, um zu gewinnen

grid_color = (161,115,81)
player1_color = (255,156,27)
player2_color = (106,199,229)
player_color_select = (255,255,255)
player_color_movable = (255,255,255)
player_color_goals = (206,168,120)
player_color_sep = (173,14,115)
player_color_noGoals = (100,100,100)
player1_color_base = (178,120,45)
player2_color_base = (121,122,123)
black = (0,0,0)
grid_color_background = (55,40,32)

# Game states und Spielphasen
stateInitialize, stateControls, stateGame, stateWin = range(4)
gameState = stateInitialize
phaseChoseMovable, phaseChoseGoal, phaseMove = range(3)

# Unwichtig
screen = pygame.display.set_mode(res)
clockObj = pygame.time.Clock()
surf_win = pygame.font.Font(None, 50).render("GEWONNEN!", True, (0,0,0))
player1_controls1_sf = pygame.font.Font(None, 30).render("Steuerung Spieler 1:", True, player1_color)
player1_controls2_sf = pygame.font.Font(None, 25).render("Auswählen: D   Bestätigen: S   Zurück: E", True, player1_color)
player2_controls1_sf = pygame.font.Font(None, 30).render("Steuerung Spieler 2:", True, player2_color)
player2_controls2_sf = pygame.font.Font(None, 25).render("Auswählen:   Pfeil nach rechts", True, player2_color)
player2_controls3_sf = pygame.font.Font(None, 25).render("Bestätigen:    Enter", True, player2_color)
player2_controls4_sf = pygame.font.Font(None, 25).render("Zurück:          Backspace", True, player2_color)
screen_controls_sf = pygame.font.Font(None, 30).render("'Leertaste' um fortzufahren", True, grid_color)


# KLASSEN DEFINITIONEN
class Game:
    def __init__(self):
        # Alle Werte veränderbar!
        self.squares_amount = 8 # Wenn < 8, dann Anfangspositionen von player2 anpassen
        self.grid_offset = 100
        self.margin = 2
        self.margin2 = 7
        self.square_width = res[0]//(self.squares_amount+4)
        self.gridReset()
        self.grid_borders = [-1, self.squares_amount]
    def gridReset(self):
        self.grid_array = [[0 for column in range(self.squares_amount)] for row in range(self.squares_amount)]
    def draw(self):
        for row in range(self.squares_amount):
            for column in range(self.squares_amount):
                # Grid
                square_posx = self.grid_offset + column*self.square_width + column*self.margin
                square_posy = self.grid_offset + row*self.square_width + row*self.margin
                square = [square_posx, square_posy, self.square_width, self.square_width]
                pygame.draw.rect(screen, grid_color, square)
                # Base Player 1
                if [column, row] in player1.base:
                    pygame.draw.rect(screen, player1_color_base, square)
                # Base Player 2
                if [column, row] in player2.base:
                    pygame.draw.rect(screen, player2_color_base, square)
                # Player 1
                for worm in player1.worms:
                    for pos in worm:
                        if column == pos[0] and row == pos[1]:
                            pygame.draw.ellipse(screen, player1.color, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin])
                            #pygame.draw.ellipse(screen, black, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin],2)
                # Player 2
                for worm in player2.worms:
                    for pos in worm:
                        if column == pos[0] and row == pos[1]:
                            pygame.draw.ellipse(screen, player2.color, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin])
                            #pygame.draw.ellipse(screen, black, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin],2)
                # Phase 1: Movable Positions
                if self.grid_array[row][column] == 1:
                    pygame.draw.ellipse(screen, player_color_movable, [square_posx+self.margin2, square_posy+self.margin2, self.square_width-2*self.margin2, self.square_width-2*self.margin2])
                # Phase 2: NORMALE Goal Positions
                if self.grid_array[row][column] in [2, 2.3]:
                    pygame.draw.ellipse(screen, player_color_goals, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin])
                # Phase 2: Goal Position bei zu durchtrennendem Wurm
                if self.grid_array[row][column] in [4, 4.3]:
                    pygame.draw.ellipse(screen, player_color_sep, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin])
                # Phase 2: SELEKTIERTE Goal Position
                if self.grid_array[row][column] in [2.3, 4.3]:
                    pygame.draw.ellipse(screen, player_color_select, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin],5)
                # Phase 2: Keine Goal Positions vorhanden
                if self.grid_array[row][column] == 5:
                    pygame.draw.ellipse(screen, player_color_noGoals, [square_posx+self.margin, square_posy+self.margin, self.square_width-2*self.margin, self.square_width-2*self.margin])

class Worm:
    def __init__(self, p1,p2,p3,p4,p5,p6, color):
        self.worms = [[p1,p2,p3,p4,p5,p6]]
        # self.worms enthält einen oder mehrere Würmer mit Positions-Paaren
        # worms[a] = ein ganzer Wurm von ev. mehreren; worms[a][b] = einzelner Stein (x- und y-Pos.) eines Wurms; worms[a][b][c] = x- oder y-Koordinate eines Steines eines Wurms
        self.color = color
        self.base = copy.deepcopy(self.worms)[0]

    def movablePositions(self):
        # = Zeige bewegbare Anfangs- und Endsteine von Würmern (=Positionen)
        pos = []
        for worm in self.worms:
            # Nur bewegbar, wenn der Wurm aus mehr als einem Stein besteht
            if len(worm) > 1:
                pos.extend([worm[0], worm[-1]])
        return pos

    def goalPositions(self, pos_goal):
        # = Zeige Positionen, zu denen der angeklickte Endstein eines Wurms sich hinbewegen könnte
        goals = []
        worm_recent = None
        goals_remove = []
        goals_sep1, goals_sep2 = [], []
        goal_temp = None
        player_recent_pos = []
        [player_recent_pos.extend(worm) for worm in player_recent.worms]
        player_other_pos = []
        [player_other_pos.extend(worm) for worm in player_other.worms]

        # 1. SUCHE DAZUGEHÖRIGEN WURM
        for worm in self.worms:
            for pos in worm:
                if pos == pos_goal:
                    worm_recent = worm
                    break
        worms_withoutRecent = self.getWormsWithoutRecent(worm_recent)

        # 2. SUCHE ANDERES ENDE VOM WURM
        if worm_recent.index(pos_goal) == 0:
            pos_move = worm_recent[-1]
        else:
            pos_move = worm_recent[0]

        # 3. BESTIMME MÖGLICHE ZIELPOSITIONEN
        goals = [[pos_goal[0]+1, pos_goal[1]], [pos_goal[0], pos_goal[1]+1], [pos_goal[0]-1, pos_goal[1]], [pos_goal[0], pos_goal[1]-1]]
        goals_dir = [[1,0], [0,1], [-1,0], [0,-1]]
        for i in range(len(goals)):
            adjacentPositions = self.getAdjacent(goals[i], worms_withoutRecent)
            # Wenn Pos AUßERHALB SPIELFELD
            if goals[i][0] in game.grid_borders or goals[i][1] in game.grid_borders:
                goals_remove.append(goals[i])
            # Wenn sich Wurm SELBST ÜBERSCHNEIDET
            elif goals[i] in worm_recent:
                goals_remove.append(goals[i])
            # Wenn sich Wurm QUADRAT-FÖRMIG berührt
            elif player_recent.getAdjacent(goals[i],[worm_recent])[2] >= 2:
                goals_remove.append(goals[i])
            # Wenn Wurm GEGNERISCHEN Wurm ÜBERSCHNEIDET
            elif goals[i] in player_other_pos:
                goal_temp = [ goals[i][0] + goals_dir[i][0], goals[i][1] + goals_dir[i][1] ]
                goals_remove.append(goals[i])
                # 1. Wenn goal_temp innerhalb Spielfeld
                if goal_temp[0] not in game.grid_borders and goal_temp[1] not in game.grid_borders:
                    # 2. Wenn goal_temp von anderem Spieler nicht besetzt
                    if goal_temp not in player_other_pos:
                        # 3. Wenn goal_temp von einem selbst nicht besetzt
                        if goal_temp not in player_recent_pos:
                            # 4. Wenn an zu durchfressendem Stein seitlich kein eig. Stein angrenzt
                            if adjacentPositions[2] == 0:
                                # 5. Wenn an goal_temp max. 1 eig. Stein angrenzt und dieser Anfang oder Ende seines Wurms ist
                                adjacentPositions = self.getAdjacent(goal_temp, worms_withoutRecent)
                                if adjacentPositions[2] <= 1:
                                    if adjacentPositions[0] == None or adjacentPositions[1].index(adjacentPositions[0]) in [0, len(adjacentPositions[1])-1]:
                                        # Durchfressen des gegn. Wurms möglich!
                                        goals_sep1.append(goals[i])
                                        goals_sep2.append(goal_temp)
            # Wenn 1 angrenzender eig. Wurm, der nicht mit einem Ende angrenzt
            elif adjacentPositions[2] == 1:
                if adjacentPositions[1].index(adjacentPositions[0]) not in [0, len(adjacentPositions[1])-1]:
                    goals_remove.append(goals[i])
            # Wenn mind. 2 eigene Würmer angrenzen
            elif adjacentPositions[2] >= 2:
                goals_remove.append(goals[i])
        # Jetzt falsche goals tatsächlich entfernen
        [goals.remove(pos) for pos in goals_remove]

        return [self.worms.index(worm_recent), pos_move, goals+goals_sep2, goals, goals_sep2, goals_sep1]

    def move(self, worm_recent_i, p_end, p_goal):
        # = bewegen und ggf. gegn. Wurm durchfressen

        # NUR BEWEGEN
        if p_goal not in goalPositions[4]:
            # 1. Zielstein am entsprechenden Ende einfügen
            if self.worms[worm_recent_i].index(p_end) == 0:
                # Wenn Zielposition am Ende des aktuellen Wurms
                self.worms[worm_recent_i].append(p_goal)
            else:
                # Wenn Zielposition am Anfang des aktuellen Wurms
                self.worms[worm_recent_i].insert(0, p_goal)
            # 2. Zu bewegenden Stein löschen
            self.worms[worm_recent_i].remove(p_end)

        # BEWEGEN + GEGNERISCHEN WURM FRESSEN
        else:
            goal_sep1_i = goalPositions[4].index(p_goal)
            worm_recent_other_i = None
            pos_other_del_i = None

            # 1. GEGN. STEIN ÜBERNEHMEN UND STEIN DAHINTER PLATZIEREN
            # Wenn Zielposition am Ende des aktuellen Wurms
            if self.worms[worm_recent_i].index(p_end) == 0:
                self.worms[worm_recent_i].extend ( [goalPositions[5][goal_sep1_i], goalPositions[4][goal_sep1_i]] )
            else:
            # Wenn Zielposition am Anfang des aktuellen Wurms
                self.worms[worm_recent_i].insert ( 0, goalPositions[5][goal_sep1_i] )
                self.worms[worm_recent_i].insert ( 0, goalPositions[4][goal_sep1_i] )
            # Eigenen Endstein löschen
            self.worms[worm_recent_i].remove(p_end)

            # 2. GEGN. STEIN LÖSCHEN
            for worm in player_other.worms:
                if goalPositions[5][goal_sep1_i] in worm:
                    worm_recent_other_i = player_other.worms.index(worm)
                    pos_other_del_i = player_other.worms[worm_recent_other_i].index(goalPositions[5][goal_sep1_i])
            player_other.worms[worm_recent_other_i].remove(goalPositions[5][goal_sep1_i])

            # 3. GEGN. WURM DURCHTRENNEN
            # Nur, wenn der Stein nicht am Anfang oder Ende des aktuellen Wurms liegt
            if pos_other_del_i not in [0, len(player_other.worms[worm_recent_other_i])]:
                worms_temp = []
                # Anfang
                if worm_recent_other_i > 0:
                    worms_temp.extend(player_other.worms[:worm_recent_other_i])
                # Mittelteil
                worms_temp.append(player_other.worms[worm_recent_other_i] [:pos_other_del_i])
                worms_temp.append(player_other.worms[worm_recent_other_i] [pos_other_del_i:])
                # Ende
                if worm_recent_other_i < len(player_other.worms)-1:
                    worms_temp.extend(player_other.worms[worm_recent_other_i+1:])
                player_other.worms = worms_temp

    def getAdjacent(self, pos, worms):
        # = returne alle Würmer, die an einen Stein angrenzen
        goals_dir = [[1,0], [0,1], [-1,0], [0,-1]]
        pos_adjacent, worm_adjacent = None, None
        touching = 0
        for direction in goals_dir:
            for worm in worms:
                if [pos[0]+direction[0], pos[1]+direction[1]] in worm:
                    pos_adjacent = [pos[0]+direction[0], pos[1]+direction[1]]
                    worm_adjacent = worm
                    touching += 1
        return [pos_adjacent, worm_adjacent, touching]

    def getWormsWithoutRecent(self,worm_recent):
        worms_withoutRecent = []
        for worm in self.worms:
            if worm != worm_recent: worms_withoutRecent.append(worm)
        return worms_withoutRecent

    def connect(self, pos_new, worm_recent):
        # = Eigene Würmer verbinden, wenn sie sich berühren
        worms_withoutRecent = self.getWormsWithoutRecent(worm_recent)
        adjacentPositions = self.getAdjacent(pos_new, worms_withoutRecent)
        # 1. Neu platzierter Stein angrenzend zu eig. anderem Wurm?
        if adjacentPositions[2] == 1:
            # 2. Neu platzierter Stein Anfang oder Ende seines Wurms?
            if self.worms[self.worms.index(worm_recent)].index(pos_new) == 0:
                # Anfang
                worm1_order = -1
            else:
                # Ende
                worm1_order = 1
            # 3. Daran angrenzender eig. Stein Anfang oder Ende des anderen eig. Wurms?
            if self.worms[self.worms.index(adjacentPositions[1])].index(adjacentPositions[0]) == 0:
                # Anfang, deshalb Reihenfolge lassen
                worm2_order = 1
            else:
                # Ende, deshalb Reihenfolge umdrehen
                worm2_order = -1
            # 4. Anderen eig. Wurm passend anfügen
            worm_temp = worm_recent[::worm1_order] + adjacentPositions[1][::worm2_order]
            worm_temp = worm_temp[::worm1_order]
            self.worms.remove(adjacentPositions[1])
            self.worms[self.worms.index(worm_recent)] = worm_temp

    def hasWon(self):
        # Spiel gewonnen, wenn mind. 5 eig. Steine in gegn. Basis
        baseWorms = 0
        for worm in self.worms:
            for pos in worm:
                if pos in player_other.base:
                    baseWorms += 1
        if baseWorms >= winCondition:
            return True

        # TO DO:
        # (?) Bei zweitem Wurm kann man nicht den gleichen Wurm nochmal steuern
        # (?) Design Fehler Till
        # Farben


# INITIALISIERUNGEN

while True:
    # GAME STATE 1: INITIALIZE
    if gameState == stateInitialize:
        game = Game() # muss als Erstes initiiert werden!
        player1 = Worm( [0,2],[0,1],[0,0],[1,0],[2,0],[3,0], player1_color ) # Reihenfolge der Argumente wichtig! (Steine nebeneinander angeordnet)
        #player1 = Worm( [5,5],[4,5],[3,5],[2,5],[1,5],[0,5], player1_color )
        player2 = Worm( [7,5],[7,6],[7,7],[6,7],[5,7],[4,7], player2_color )
        player_recent = player1
        player_other = player2

        # Tastenbelegung
        select, confirm, back = range(3)

        player_keys = {
        player1:{
        select  : pygame.locals.K_RIGHT,
        confirm : pygame.locals.K_RETURN,
        back    : pygame.locals.K_BACKSPACE},
        player2:{
        select  : pygame.locals.K_d,
        confirm : pygame.locals.K_s,
        back    : pygame.locals.K_e}}

        # Diverses
        movablePositions = None
        goalPositions = None
        player_turns = 0
        counter = -1
        counter_last = None
        worms_amount = 0

        # Zum Controls-Screen übergehen
        gameState = stateControls
        gamePhase = phaseChoseMovable

    # GAME STATE 2: CONTROLS SCREEN
    if gameState == stateControls:
        clockObj.tick(framerate)

        screen.fill(grid_color_background)
        screen.blit(player1_controls1_sf, [res[0]/8, res[1]/4])
        screen.blit(player1_controls2_sf, [res[0]/20, res[1]/3])
        screen.blit(player2_controls1_sf, [res[0]/8*5, res[1]/4])
        screen.blit(player2_controls2_sf, [res[0]/20*12, res[1]/3])
        screen.blit(player2_controls3_sf, [res[0]/20*12, res[1]/30*11])
        screen.blit(player2_controls4_sf, [res[0]/20*12, res[1]/30*12])
        screen.blit(screen_controls_sf, [res[0]/3, res[1]/4*3])
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                gameState = stateGame

    # MAIN-LOOP
    while gameState == stateGame:
        # GAME STATE 3: GAME

        #Framerate
        clockObj.tick(framerate)

        #Events -> funzt nicht, da später 2. event-Schleife
        '''for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()'''

        # SPIEL-PHASEN

        # PHASE 1: ZU BEWEGENDEN STEIN AUSWÄHLEN
        if gamePhase == phaseChoseMovable:
            if movablePositions == None:
                movablePositions = player_recent.movablePositions()
                # MovablePositions in Grid Array eintragen
                if movablePositions != []:
                    game.grid_array[movablePositions[counter][1]][movablePositions[counter][0]] = 1
                else:
                    gameState = stateWin
                # Anzahl der Züge festlegen
                player_turns_max = len(movablePositions)//2
            for event in pygame.event.get():
                # 1. Wurm-Ende auswählen
                if event.type == KEYDOWN and event.key == player_keys[player_recent][select]:
                    counter = (counter + 1)%len(movablePositions)
                    game.gridReset()
                    game.grid_array [movablePositions[counter][1]] [movablePositions[counter][0]] = 1
                # 2. Bestätigen
                if event.type == KEYDOWN and event.key == player_keys[player_recent][confirm] and counter > -1:
                    gamePhase = phaseChoseGoal
                    break

        # PHASE 2: ZIELPOSITION AUSWÄHLEN
        if gamePhase == phaseChoseGoal:
            if goalPositions == None:
                goalPositions = player_recent.goalPositions(movablePositions[counter])
                game.gridReset()
                # Zielpositionen in Grid eintragen
                for pos in goalPositions[2]:
                    if pos in goalPositions[3]:
                        # Zielstein am eig. Wurm
                        game.grid_array[pos[1]][pos[0]] = 2
                    else:
                        # Zielstein hinter gegn. Wurm
                        game.grid_array[pos[1]][pos[0]] = 4
                counter_last = counter
                if len(goalPositions[2]) != 0: counter = (counter + 1)%len(goalPositions[2])
            for event in pygame.event.get():
                # Wenn keine Zielpositionen vorhanden: Bewegung nicht möglich
                if len(goalPositions[2]) == 0:
                    game.grid_array[movablePositions[counter_last][1]][movablePositions[counter_last][0]] = 5
                else:
                    # 1. Zielposition auswählen
                    if event.type == KEYDOWN and event.key == player_keys[player_recent][select]:
                        counter = (counter + 1)%len(goalPositions[2])
                        if goalPositions[2][counter] in goalPositions[3]:
                            game.grid_array[goalPositions[2][counter][1]][goalPositions[2][counter][0]] = 2.3
                        else:
                            game.grid_array[goalPositions[2][counter][1]][goalPositions[2][counter][0]] = 4.3
                        if len(goalPositions[2]) > 1:
                            if goalPositions[2][counter-1] in goalPositions[3]:
                                game.grid_array[goalPositions[2][counter-1][1]][goalPositions[2][counter-1][0]] = 2
                            else:
                                game.grid_array[goalPositions[2][counter-1][1]][goalPositions[2][counter-1][0]] = 4
                    # 2. Bestätigen
                    if event.type == KEYDOWN and event.key == player_keys[player_recent][confirm]:
                        gamePhase = phaseMove
                # 3. Einen Schritt zurück gehen
                if event.type == KEYDOWN and event.key == player_keys[player_recent][back]:
                    game.gridReset()
                    gamePhase = phaseChoseMovable
                    movablePositions, goalPositions = None, None
                    counter = counter_last

        # PHASE 3: WURM BEWEGEN
        if gamePhase == phaseMove:
            # Bewegen
            player_recent.move(goalPositions[0],goalPositions[1],goalPositions[2][counter])
            # Ev. getrennte Würmer verbinden
            player_recent.connect(goalPositions[2][counter], player_recent.worms[goalPositions[0]])
            # Ev. Spielzüge verringern
            for worm in player_recent.worms:
                if len(worm) > 1:
                    worms_amount += 1
            if worms_amount < player_turns_max:
                player_turns_max -= 1
            # Nächster Zug wenn Spiel nicht gewonnen
            if not player_recent.hasWon():
                # Alles resetten
                game.gridReset()
                movablePositions, goalPositions, counter, worms_amount = None, None, 0, 0
                # Nächster Zug
                player_turns += 1
                gamePhase = phaseChoseMovable
            else:
                gameState = stateWin

        # GAME STATE 4: SPIEL GEWONNEN
        if gameState == stateWin:
            screen.blit(surf_win, [res[0]/2-surf_win.get_width()/2, res[1]/2-surf_win.get_height()/2])
            pygame.display.update()
            pygame.time.wait(5000)
            # Neues Spiel
            gameState = stateInitialize

        # Spieler wechseln
        if player_turns >= player_turns_max:
            player_turns = 0
            if player_recent == player1:
                player_recent = player2
                player_other = player1
            else:
                player_recent = player1
                player_other = player2

        # Alles zeichnen
        screen.fill(grid_color_background)
        game.draw()
        pygame.display.update()




# FEHLER DOKUMENTATION:
# Verschachtelter Index falsch
# Variable an falscher Stelle initiiert
# Werte der List Comprehension nicht übergeben
# Liste 4 Elemente zugefügt, dann 4er-for-Schleife, die den Index der Liste abfragt und in der Elemente der Liste gelöscht werden -> Fehlermeldung, weil Liste verkürzt und Indizierung nicht mehr möglich
# 2 Eventschleifen hintereinander klappen nicht; variable für events.get() speichert events und kickt sie nicht wieder aus der queue
# 2x vergessen Variablen zu resetten
# Variable nicht zurückgesetzt (player_turns)
# Versucht Attribut von Instanz zu iterieren, dabei Instanz iteriert und Attribut vergessen
# "list index out of range"-Meldung: Komma bei Liste vergessen
# bei verschachtelter Liste zu viele Klammern
# bei x-y-Liste Zahlen verdreht
# Klammer vergessen; Methode nicht auf Instanz angewendet
# Logik-Fehler: den gleichen Stein zwei mal removed, dadurch später Fehlermeldung
# Code-Zeile übersehen, die völligen Humbug berechnet hat
# Probleme mit Bearbeitung von verschachtelten Listen
# Klammer-Fehler bei len()-1
# zur Indizierung Variable des falschen Spielers verwendet
# for-Schleife mit if-Bedingung falsch verwendet
# vergessen beim Durchfressen eig. Endstein zu löschen
# in einer Zeile Liste erstellen ([a,b]), Slicen und Extenden klappt nicht (?)
# Werte bei Methodenaufrufe nicht übergeben
# Methode logisch falsch
# pygame.event.get() verwendet lokale Variablen (z.B. K_RETURN), die nur innerhalb der Event-Schleife gültig sind; Dictionary mit z.B. K_RETURN als Value klappt somit nicht, benötigt pygame.locals.K_RETURN
# Schreibfehler (K_KETURN)
# Methode zu weit eingerückt, Instanz hatte somit kein "hasWon-Attribut"
# Code eingefügt, der kurz danach überschrieben wurde
# Klammer-Fehler bei Indizierung von len() -> "int-Obj not substribtible"

# DURCH PROGRAMMIERUNG DIESES SPIELS TRAINIERTE BEREICHE:
# Logisches Denken
# verschachtelte Listen / Indizierungen
# for-Schleifen
# Prozesse formalisieren

# NÄCHSTES MAL ANDERS MACHEN:
# Übergabewerte von Methoden übersichtlicher sortieren, vllt weniger pro Methode
