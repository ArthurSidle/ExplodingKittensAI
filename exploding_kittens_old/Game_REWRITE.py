# imports all the modules needed 
import random
import tkinter as tk
import WelcomeTEST as WT
import Check_Card_Played as CCP
import Check_Card_Drawn as CCD
import Draw_Pile_Command as DPC
import Deal_To_Com_Players as dtcp
import Com1_Behavior as C1B
import Com2_Behavior as C2B
import Com3_Behavior as C3B
import Check_Com1_Card_Played as CC1CP
import Check_Com2_Card_Played as CC2CP
import Check_Com3_Card_Played as CC3CP
from tkinter import messagebox

# Creates the Tk Window
gameScreen = tk.Tk()
gameScreen.title("Exploding Kittens Game") # Renames the windows to: Exploding Kittens Game
gameScreen.geometry("1366x800") # Sets the bg color
gameScreen.configure(bg = '#00FFFF') # Sets the size
gameScreen.resizable(0, 0) # Makes so the window is not resizable

# Creates a list containing all the cards in the game
cards = ['nope', 'attack', \
        'skip', 'favor', 'shuffle', 'see the future', 'potato cat', \
        'taco cat', 'rainbow ralphing \n cat', 'beard cat', 'cattermellon']

# Bollens to check if a card was played
card_played = [None] * 7

com1_turn  = False
com2_turn = False
com3_turn = False
player_turn = True

reserve_cards = [" "] * 8

exploding_kittens_card_drawn = False # Stores is a exploding kitten card is drawn

# Functions Needed
def exit_app():
    # Exits the app

    MsgBox = messagebox.askquestion ('Exploding Kittens Game','Are you sure you want to exit?', icon = 'warning') # Asks the player if they want to quit
    
    # Checks if the player clicked on "yes"
    if MsgBox == 'yes':
       gameScreen.destroy()
       exit()

def add_to_reserve_cards():
    global player_turn

    # When the player draws, but they played no cards this will fill an empty section in the reserve hand

    for i in range(0, 8):
        # Checks if there is an empty slot in the list 
        if reserve_cards[i] == " ":
            # Assigns the slot a random choice from the cards list
            reserve_cards[i] = random.choice(cards)
            # Tells the player which card they got
            messagebox.showinfo("Exploding Kittens Game", "Heres your new card: " + reserve_cards[i] + ", it was added to your reserve hand (to access it first play a card then draw)")
            break
        if i == 7:
            # Tells the player that they reached the limit of cards that they can have in their reserve hand
            messagebox.showerror("Exploading Kittens Game", "You have to many cards in your reserve hand. You can hold up to 8 cards")

    player_turn = False # Sets the players turn to false

def card_command(card_number):
    global card_played

    # Checks if its the players turn
    if player_turn == True:
        discard_pile_text.set(f"{CARDS_IN_HAND[card_number]}\n \n \n") # Sets the discard pile display text to the card that you've played 
        show_card[card_number].destroy() # Destroys the card

        card_played[card_number] = True # Sets the bollen from the Game_REWRITE script to True 

        player_cards[0] = "" # Re-Assigns the slot in the list to match that the played card

        CCP.check_card_to_play(CARDS_IN_HAND[card_number]) # Checks the card, so it can do its respected function
    else:
        for com in (C1B, C2B, C3B):
            if com.card_to_play == "favor":
                if com == C1B:
                    com_number = '1'
                    check_com = CC1CP
                elif com == C2B:
                    com_number = '2'
                    check_com = CC2CP
                elif com == C3B:
                    com_number = '3'
                    check_com = CC3CP

                # Asks the player for if they a sure they want to give that card to com 1
                favoraction = messagebox.askyesno("Exploding Kittens Game",
                                                  f"Are you sure you want to give com{com_number} your {CARDS_IN_HAND[card_number]}", icon = "warning")

                # Checks if the player clicked on "yes"
                if favoraction == True:
                    # Tells the player that their card was add to com 1's hand
                    messagebox.showinfo("Exploding Kittens Game",
                                        f"You have given com{com_number} your {CARDS_IN_HAND[card_number]}")
                    
                    card1_played = True  # Makes the bollen False

                    com.card_to_play = "" # Sets com 1's card to play to an empty string so the the next time the player goes to click on another card this if statement doesn't repeat

                    show_card[card_number].destroy() # Destroys the card

                    player_cards[0] = "" # Re-Assigns the slot in the list to match that the played card

                    check_com.get_favor_or_stolen_card(CARDS_IN_HAND[card_number])
                    check_com.draw_card() # Makes com 1 draw a card

                else:
                    # Tells the player that the card that they clicked on wasn't given to com 1
                    messagebox.showerror("Exploding Kittens Game", f"You have not given your card to com{com_number}")
                
                break

            if com == C3B:
                # Tells the player that it's not their turn
                messagebox.showerror('Exploding Kittens Game', "Sorry, it's not your turn")

# Helper function to assign unique lambda expressions to button commands
def get_card_command(card_number):
    return lambda: card_command(card_number)

# Function for the players diffuse card
def play_diffuse_card():
    global exploding_kittens_card_drawn

    if exploding_kittens_card_drawn == False:
        messagebox.showerror("Exploding Kittens Game", "You cant play you diffuse card unless you have drawn an Exploding Kittens card")
    else:
        messagebox.showinfo("Exploding Kittens Game", "You have diffused the Exploding Kitten card!")

        exploding_kittens_card_drawn = True

def show_com_players():
    if WT.com_number == 1:
        display_com_1 = tk.Label(gameScreen, text = "COM 1", font = "15")
        display_com_1.place(y =0, x = 650) 

        dtcp.com1_amount1()
    elif WT.com_number == 2:
        display_com_1 = tk.Label(gameScreen, text = "COM 1", font = "15")
        display_com_1.place(y =400, x = 0)
        display_com_2 = tk.Label(gameScreen, text = "COM 2", font = "15")
        display_com_2.place(y = 400, x = 1300) 

        dtcp.com1_amount2()
        dtcp.com2_amount2()
    elif WT.com_number == 3:
        display_com_1 = tk.Label(gameScreen, text = "COM 1", font = "15")
        display_com_1.place(y =400, x = 0) 
        display_com_2 = tk.Label(gameScreen, text = "COM 2", font = "15")
        display_com_2.place(y = 0, x = 650)
        display_com_3 = tk.Label(gameScreen, text = "COM 3", font = "15")
        display_com_3.place(y = 400, x = 1300) 
         
        dtcp.com1_amount3()
        dtcp.com2_amount3()
        dtcp.com3_amount3()

## Shows username
usernameLabel = tk.Label(gameScreen, text = WT.username, font = "15")
usernameLabel.place(x = 650, y = 660)

show_com_players()

## Chose + Show cards
CARDS_IN_HAND = [None] * 7
for i in range(0, 8):
    CARDS_IN_HAND[i] = random.choice(cards)
    CCD.check_card(CARDS_IN_HAND[i]) # Checks the card drawn

# Creates a list containing all player cards
player_cards = CARDS_IN_HAND.copy()

## Shows cards in tk window
show_card = [None] * 7
show_card_pos = ((650, 600), (810, 600), (960, 600), (1090, 600), (170, 600), (330, 600), (490, 600))
for i in range(0, 8):
    show_card[i] = tk.Button(gameScreen, text = CARDS_IN_HAND[i], font = "20", command = get_card_command(i))
    show_card[i].place(x = show_card_pos[i][0], y = show_card_pos[i][1])

# Displays the diffuse card to the player
diffuse_card = tk.Button(gameScreen, text="Diffuse", font="20", command=play_diffuse_card)
diffuse_card.place(x = 650, y = 560)

CCD.check_card("diffuse")

## Shows draw and discard piles
draw_pile = tk.Button(gameScreen, text = "Draw \n \n Pile", font = "Arial 50" , bg  = "red", command = DPC.draw_card)
draw_pile.place(x = 400, y = 200)

discard_pile_text = tk.StringVar()
discard_pile = tk.Label(gameScreen, textvariable = discard_pile_text, font = "Arial 30", bg  = "red")
discard_pile.place(x = 800, y = 200)
discard_pile_text.set("Discard \n \n Pile")

# Quit button
quit_button = tk.Button(gameScreen, text = "QUIT", command = exit_app)
quit_button.place(x = 0, y = 0)

messagebox.showinfo("Exploding Kittens Game", "It is currently your turn.")

gameScreen.mainloop()
