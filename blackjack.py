25000
print("""ABOUT THE GAME
Objective:
The objective of Blackjack is to beat the dealer by having a hand value closer to 21 than the dealer’s hand without exceeding 21.
Equipment:
Standard 52-card deck without jokers. Multiple decks may be used, typically 6-8 decks in a casino setting.
Card Values:
- Number cards (2-10): Face value
- Face cards (Jack, Queen, King): 10 points each
- Ace: 1 point or 11 points (player's choice, whichever is preferable without busting)
Game Flow:
1. **Initial Deal:**
   - Each player is dealt two cards face up.
   - The dealer receives one card face up (upcard) and one card face down (hole card).
2. **Player’s Turn:**
   - Players decide whether to "hit" (receive another card) or "stand" (keep current hand).
   - Players can also choose to "double down" (double their bet and receive exactly one more card) or "split"
   (if dealt two cards of the same rank, split them into two separate hands, each with its own bet).
3. **Dealer’s Turn:**
   - After all players have completed their turns, the dealer reveals the hole card.
   - The dealer must hit until the total is 17 or higher.
   This rule may vary (e.g., some casinos require the dealer to hit on "soft 17" – a hand containing an Ace counted as 11).
4. **Determine Winner:**
   - If the player’s total is closer to 21 than the dealer’s total without exceeding 21, the player wins.
   - If the dealer busts (exceeds 21), all remaining players win.
   - If both player and dealer have the same total, it’s a "push" (tie), and the player’s bet is returned.
Special Hands:
- **Blackjack:** A two-card hand totaling 21 (e.g., Ace + 10-value card) is called a Blackjack.
It usually pays 3:2 unless the dealer also has a Blackjack, in which case it’s a push.
- **Insurance:** If the dealer’s upcard is an Ace, players can make an additional bet (up to half of their original bet) that the dealer has a Blackjack.
If the dealer has a Blackjack, the insurance bet pays 2:1.

Betting:
- Players place bets before any cards are dealt.
- Minimum and maximum bets are typically posted at each table.

Variations and Additional Rules:
- **Surrender:** Some casinos allow players to surrender their hand and forfeit half of their bet after the initial deal.
- **Double Down:** Players may be allowed to double their bet after seeing their initial two cards and receive exactly one additional card.
- **Splitting:** Rules may vary on whether and how many times players can split their hands, especially when Aces are involved.

Etiquette:
- Follow table rules and gestures (e.g., tapping the table to hit, waving hand to stand).
- Avoid touching cards once they are dealt unless instructed by the dealer.

Dealer Rules:
- Dealers follow specific rules set by the casino regarding when to hit or stand.""")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
import random

def card(card_values):
    return random.choice(card_values)

def check(currency, bet, tpoints, dtpoints):
    if tpoints <= 21:
        if dtpoints <= 21:
            if dtpoints > tpoints:
                print("YOU LOST")
                currency -= bet
            elif dtpoints < tpoints:
                print("YOU WIN")
                currency += bet
            else:
                print("DRAW (PUSH)")
        elif dtpoints > 21:
            print("YOU WIN")
            currency += bet
    elif tpoints > 21:
        print("YOU LOSE")
        currency -= bet
    return currency

def adjust_for_ace(total, num_aces):
    while total > 21 and num_aces > 0:
        total -= 10
        num_aces -= 1
    return total

def stand(card_dealer, card_values, tpoints, dtpoints):
    print("The dealer's cards are:", card_dealer)
    while dtpoints < 17:
        ndcard = card(card_values)
        card_dealer.append(ndcard)
        dtpoints += ndcard
        dtpoints = adjust_for_ace(dtpoints, card_dealer.count(11))
    return dtpoints

def hit(tpoints, card_values, card_player):
    ncard = card(card_values)
    card_player.append(ncard)
    tpoints += ncard
    tpoints = adjust_for_ace(tpoints, card_player.count(11))
    print("The new set of cards are", card_player)
    return tpoints

card_dealer = []
card_player = []
currency = 2500
bet = 0
card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
z = True

while z:
    card_player.clear()
    card_dealer.clear()
    card1 = card(card_values)
    card2 = card(card_values)
    card_player.extend([card1, card2])
    card3 = card(card_values)
    card4 = card(card_values)
    card_dealer.extend([card3, card4])

    print("You have total", currency, "to use")
    bet = int(input("Enter amount to bet:"))
    print("Your hand of cards include:", card1, card2)
    tpoints = card1 + card2
    print("The dealer's hand of cards include:", card3, "and one more card")

    dtpoints = card3 + card4

    while tpoints < 21:
        c = input("What would you do, Hit, Stand: ").capitalize()
        if c == "Hit":
            tpoints = hit(tpoints, card_values, card_player)
        elif c == "Stand":
            dtpoints = stand(card_dealer, card_values, tpoints, dtpoints)
            break

    currency = check(currency, bet, tpoints, dtpoints)
    z = input("Wanna go on another round? (yes/no): ").lower() == "yes"

print("Game over! You have", currency, "left.")