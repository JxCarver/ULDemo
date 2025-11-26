Demo set up for a ProxMark3/Easy to read and program a MiFare Ultralight card to a new scanner.


Below are the instructions that were given to the others who needed to give the demo.


#BASIC DEMO (Do this most of the time)

cd proxmark3

#Enter the proxmark3 directory

pm3

#Run the program

hf search

#Will need to be run for each card. Scans most NFC cards and tags. See Things to Say section for information to give people. If thre are no results, ctrl+C and try lf search. If still no results, see list of possible reasons for no scan


#############################################################################################################


#Scan && Add && Emulate Demo (Do this if a card is shown to be MiFare Ultralight or Mifare Hospitality

cd ..

#Return to home directory

source pn532env/bin/activate

#ONLY DO THIS IF NOT ALREADY IN A VIRTUAL ENVIRONMENT

#Place the card on the Proxmark. 

./ULDemo.sh

#If you get a bad scan ctrl+C and try again.

#Place the card onto the red module, a popup should appear saying "Access Granted" and specifying how many pages were read. If this does not happen, you fucked up and are dumb.

#On the Flipper Zero navigate to Apps>NFC>Read. Scan the card. If all pages were read, the card is unencrypted and can be emulated. Either way, click the emulate button and scan the flipper with the red module.
# Tell them if the card is encrypted or not. The flipper should tell you how many total pages are encrypted.

# If a command is not working, call J. If an error message repeats and you don't know why, call J. If Deviant Ollam shows up, Call J. If it says to call J, Call J.


####################################################################################################################

#POSSIBLE REASON FOR NO SCAN

#1. Card/tag is not NFC. Check for a magstrip.
#2. Card/tag is damaged, visually inspect.
#3. Card/tag was moved from the scanner too quickly. Let both commands finish.

####################################################################################################################

#THINGS TO SAY:

#MiFare DesFire: Modern security, when used correctly nearly uncrackable. Uses AES encryption, would take every computer on the planet billions of years to crack the encryption.

#MiFare Classic: Outdated, worked well in 1994 when it was created, but since CRYPTO1(MiFare proprietary encryption) was cracked in 2008, cards can be fully cloned.

#MiFare Ultralight: Cheap and easy to use at the cost of security. Encryption can typically be cracked, many cards are unencrypted. Both the proxmark and flipper can scan for this.

#EM4100: Plaintext and unencrpyted. Can be cloned by an advanced microwave. beep beep.

#HID Prox: No real encryption, relies on security by obscurity.

#Anything else: Note what it is and send it to me. I will update when I get the chance. Proxmark should give details as to what protocol is used, what parts are encrypted, and more. Make it a learning experience and read the screen.
