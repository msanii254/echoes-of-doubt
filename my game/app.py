from flask import Flask, render_template, request, session, redirect, url_for
import os
import random

app = Flask(__name__)
# Generate a strong secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# --- Game Logic Class (as provided by you, with minor adjustments) ---
class GameLogic:
    def __init__(self):
        self.scenarios = self._build_scenarios()
        self.total_levels = max(self.scenarios.keys()) # Dynamically get total levels

    def _build_scenarios(self):
        return {
            # --- PHASE 1: The Descent ---
            1: {
                'description': (
                    "You wake in a stone room. A rusty key glints on the floor. "
                    "The torchlight flickers in a rhythm that matches your childhood nightlight."
                ),
                'options': {
                    'a': "Take the key - it might open the door",
                    'b': "Ignore the key - it feels wrong",
                    'c': "Break the torch free - light is safety",
                    'd': "Call for help - surely someone hears"
                },
                'consequences': {
                    'a': {'immediate': "The key fits but resists turning. The door creaks open.", 'delayed_reveal_level': 5, 'is_wrong': False},
                    'b': {'immediate': "The whispers grow louder. The key vibrates slightly.", 'delayed_reveal_level': None, 'is_wrong': False}, # No delayed message for this 'wrong' path
                    'c': {'immediate': "The torch comes free. The shadows twist violently.", 'delayed_reveal_level': 7, 'is_wrong': True},
                    'd': {'immediate': "Something echoes your call... but the voice isn't yours.", 'delayed_reveal_level': 3, 'is_wrong': True}
                }
            },

            2: {
                'description': "The corridor walls bleed black sludge. Portraits' eyes track you. Three paths: left (rot smell), right (whispers), center (silent).",
                'options': {
                    'a': "Left - follow the stench",
                    'b': "Right - toward the whispers",
                    'c': "Center - embrace silence",
                    'd': "Go back - this place is wrong"
                },
                'consequences': {
                    'a': {'immediate': "The air thickens. Your skin crawls.", 'delayed_reveal_level': 10, 'is_wrong': True},
                    'b': {'immediate': "The whispers form words: 'Turn back while you can'", 'delayed_reveal_level': 4, 'is_wrong': True},
                    'c': {'immediate': "The silence presses on your eardrums.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'd': {'immediate': "The door is gone. Only a bloodstained wall remains.", 'delayed_reveal_level': 2, 'is_wrong': True}
                }
            },

            # --- PHASE 2: Reality Shifts ---
            3: {
                'description': (
                    "A bathroom where the mirror shows your reflection smiling. "
                    "The bathtub is filled with dark liquid. The mirror fog clears just enough "
                    "to show a familiar bedroom reflected behind you."
                ),
                'options': {
                    'a': "Wipe the mirror - confront your reflection",
                    'b': "Touch the liquid - is it blood?",
                    'c': "Search for the music box",
                    'd': "Leave immediately"
                },
                'consequences': {
                    'a': {'immediate': "Your reflection mouths: 'Help me'. The glass frosts over.", 'delayed_reveal_level': 4, 'is_wrong': True},
                    'b': {'immediate': "It sticks like syrup. The level begins rising.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "The sound moves. It's following you.", 'delayed_reveal_level': 6, 'is_wrong': True},
                    'd': {'immediate': "The door slams shut. The music stops.", 'delayed_reveal_level': 3, 'is_wrong': False} # Correct choice for secret ending
                }
            },

            4: {
                'description': "A library where every book is titled with your name. One lies open, describing your exact movements... up to this moment.",
                'options': {
                    'a': "Read ahead - see your future",
                    'b': "Burn the book - destroy this invasion",
                    'c': "Search for the author",
                    'd': "Run - you don't want to know"
                },
                'consequences': {
                    'a': {'immediate': "The next page reads: 'NOW IT SEES YOU TOO.'", 'delayed_reveal_level': 8, 'is_wrong': True},
                    'b': {'immediate': "The flames turn blue. The other books whisper.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'c': {'immediate': "You find your own handwriting.", 'delayed_reveal_level': 5, 'is_wrong': True},
                    'd': {'immediate': "The books rearrange to block your exit.", 'delayed_reveal_level': 2, 'is_wrong': False}
                }
            },

            5: {
                'description': "A dining room set for a feast. The food moves when you blink. The chair at the head pulls itself out, inviting you.",
                'options': {
                    'a': "Sit at the head - accept the invitation",
                    'b': "Eat the food - it smells like childhood meals",
                    'c': "Overturn the table - reject this mockery",
                    'd': "Back away slowly"
                },
                'consequences': {
                    'a': {'immediate': "The other chairs creak. Something sits down.", 'delayed_reveal_level': 9, 'is_wrong': True},
                    'b': {'immediate': "It's warm. You hear chewing from the walls.", 'delayed_reveal_level': 12, 'is_wrong': True},
                    'c': {'immediate': "The plates reassemble. More place settings appear.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'd': {'immediate': "The door handle turns by itself.", 'delayed_reveal_level': 5, 'is_wrong': True}
                }
            },

            6: {
                'description': "A nursery with a rocking chair moving on its own. The mobile above the crib spins too fast. A lullaby plays backwards.",
                'options': {
                    'a': "Rock the crib - comfort the unseen",
                    'b': "Stop the chair - break the cycle",
                    'c': "Examine the mobile - the shapes look familiar",
                    'd': "Cover your ears - block the lullaby"
                },
                'consequences': {
                    'a': {'immediate': "A tiny hand grabs your finger. The crib is empty.", 'delayed_reveal_level': 7, 'is_wrong': True},
                    'b': {'immediate': "It fights you. The wood feels like skin.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "The shapes are bones. They rattle as they spin.", 'delayed_reveal_level': 10, 'is_wrong': False}, # Correct choice for secret ending
                    'd': {'immediate': "The lullaby continues inside your skull.", 'delayed_reveal_level': 4, 'is_wrong': True}
                }
            },

            # --- PHASE 3: The House's Secrets ---
            7: {
                'description': "A greenhouse with no exit. The plants twitch. One flower blooms with your face, its petals whispering secrets.",
                'options': {
                    'a': "Take the silver key from the flower's mouth",
                    'b': "Water the plants - they seem thirsty",
                    'c': "Uproot your face-flower - destroy it",
                    'd': "Scream - release the tension"
                },
                'consequences': {
                    'a': {'immediate': "The flower bites your hand. The key sticks.", 'delayed_reveal_level': 11, 'is_wrong': True},
                    'b': {'immediate': "They drink eagerly. Vines creep toward you.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'c': {'immediate': "It shrieks. The other plants turn toward you.", 'delayed_reveal_level': 14, 'is_wrong': True},
                    'd': {'immediate': "The glass cracks. Black liquid seeps in.", 'delayed_reveal_level': 6, 'is_wrong': True}
                }
            },

            8: {
                'description': "A classroom with 20 empty desks. The chalkboard writes itself: 'YOUR MISTAKES WILL BE CORRECTED'.",
                'options': {
                    'a': "Erase the board - defy the message",
                    'b': "Sit at desk #13 - your childhood number",
                    'c': "Break the chalk - stop the writing",
                    'd': "Answer the board - write back"
                },
                'consequences': {
                    'a': {'immediate': "The chalk reappears. The words rewrite faster.", 'delayed_reveal_level': 9, 'is_wrong': True},
                    'b': {'immediate': "The desk shackles clamp your wrists.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "Your hands fill with chalk dust. It won't wash off.", 'delayed_reveal_level': 15, 'is_wrong': True},
                    'd': {'immediate': "The board responds: 'GOOD STUDENT'", 'delayed_reveal_level': 7, 'is_wrong': False}
                }
            },
            9: {
                'description': "A vast, echoing ballroom. Dust motes dance in faint light. The phantom sound of music and laughter swells, then fades. A single, pristine red rose lies on the polished floor.",
                'options': {
                    'a': "Pick up the rose - it's the only splash of color",
                    'b': "Try to dance - perhaps the sound will return",
                    'c': "Search for the source of the music",
                    'd': "Leave the rose - nothing is truly 'safe' here"
                },
                'consequences': {
                    'a': {'immediate': "Thorns dig into your hand. The rose feels cold, unnatural.", 'delayed_reveal_level': 12, 'is_wrong': True},
                    'b': {'immediate': "The music starts, but it's a discordant, mocking waltz.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "The music leads you in circles, always just out of reach.", 'delayed_reveal_level': 13, 'is_wrong': False},
                    'd': {'immediate': "As you turn, the rose vanishes. A shadow darts where it lay.", 'delayed_reveal_level': 8, 'is_wrong': False}
                }
            },
            10: {
                'description': "A dark, cramped crawlspace. The air is stale and thick with the smell of old wood and something else... something sweet and sickly. Small, glistening eyes peek from the darkness.",
                'options': {
                    'a': "Crawl forward into the darkness",
                    'b': "Try to find a light source",
                    'c': "Bang on the walls - make some noise",
                    'd': "Close your eyes and wait"
                },
                'consequences': {
                    'a': {'immediate': "Something brushes your face. It feels like fur... or hair.", 'delayed_reveal_level': 14, 'is_wrong': True},
                    'b': {'immediate': "Your hand finds a rusty lever. A faint light reveals grotesque carvings.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'c': {'immediate': "A chorus of whispers echoes your banging, growing louder.", 'delayed_reveal_level': 11, 'is_wrong': True},
                    'd': {'immediate': "The glistening eyes draw closer. You feel breath on your skin.", 'delayed_reveal_level': 9, 'is_wrong': True}
                }
            },
            11: {
                'description': "A child's bedroom, but everything is subtly wrong. The toys are arranged in menacing poses, facing the door. The bedsheets are stained with what looks like mud, but smells of fear.",
                'options': {
                    'a': "Rearrange the toys - make them friendly",
                    'b': "Check under the bed - where is the child?",
                    'c': "Open the closet - a hiding spot?",
                    'd': "Flee this unsettling room"
                },
                'consequences': {
                    'a': {'immediate': "The toys snap back to their original positions as you move away.", 'delayed_reveal_level': 15, 'is_wrong': True},
                    'b': {'immediate': "A pair of glowing eyes stare back from the darkness.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "A small, rusted key lies on the closet floor. A faint moan comes from within.", 'delayed_reveal_level': 10, 'is_wrong': False},
                    'd': {'immediate': "The door handle is searing hot. You're trapped.", 'delayed_reveal_level': 12, 'is_wrong': True}
                }
            },

            # --- PHASE 4: Doppelgängers ---
            12: {
                'description': "You're back in the first room. Another 'you' stands across from you, reaching for the key. It screams silently when it sees you.",
                'options': {
                    'a': "Attack it - this imposter must die",
                    'b': "Let it take the key - observe",
                    'c': "Communicate - maybe it's friendly",
                    'd': "Close your eyes - this can't be real" # Correct choice for secret ending
                },
                'consequences': {
                    'a': {'immediate': "Your hands pass through. It points behind you.", 'delayed_reveal_level': 15, 'is_wrong': True},
                    'b': {'immediate': "It unlocks the door. The scream isn't human.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "It mouths words. You have no shadow.", 'delayed_reveal_level': 18, 'is_wrong': True},
                    'd': {'immediate': "It's inches from your face when you open them.", 'delayed_reveal_level': 6, 'is_wrong': False}
                }
            },
            13: {
                'description': (
                    "A circular room filled with ticking clocks, all showing different times. "
                    "One grandfather clock's pendulum swings erratically, its glass revealing "
                    "a childhood photo of you behind the gears. The air smells of burnt hair."
                ),
                'options': {
                    'a': "Adjust the clocks to match your birth time",
                    'b': "Smash the grandfather clock - stop the noise",
                    'c': "Retrieve the photo - why is it here?",
                    'd': "Cover your ears - the ticking is maddening"
                },
                'consequences': {
                    'a': {'immediate': "The clocks chime in unison. Your vision blurs.", 'delayed_reveal_level': 16, 'is_wrong': True},
                    'b': {'immediate': "Blood oozes from the cracks. The photo smiles.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "The gears snag your sleeve. The clock face shows your age at death.", 'delayed_reveal_level': 19, 'is_wrong': True},
                    'd': {'immediate': "The ticks become heartbeats. They match your pulse.", 'delayed_reveal_level': 8, 'is_wrong': False}
                }
            },
            14: {
                'description': (
                    "A chapel made entirely of bones. The pews are rib cages, the altar a skull. "
                    "A bone key rests on the pulpit. The hymnbook's pages are made of skin with "
                    "lyrics in your handwriting."
                ),
                'options': {
                    'a': "Take the bone key - it might be important",
                    'b': "Read the hymnbook - whose skin is this?",
                    'c': "Kneel at the altar - show respect",
                    'd': "Vandalize the chapel - reject this sacrilege"
                },
                'consequences': {
                    'a': {'immediate': "The key fuses to your palm. The bones rattle.", 'delayed_reveal_level': 17, 'is_wrong': True},
                    'b': {'immediate': "The words rearrange into your childhood diary entries.", 'delayed_reveal_level': 9, 'is_wrong': False},
                    'c': {'immediate': "Something cold presses on your shoulders from behind.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'd': {'immediate': "The bones reassemble into a towering figure.", 'delayed_reveal_level': 12, 'is_wrong': True}
                }
            },
            15: {
                'description': (
                    "A workshop filled with porcelain dolls in various states of completion. "
                    "One unfinished doll has your face. Its hollow chest cavity contains "
                    "a tiny beating heart connected to strings."
                ),
                'options': {
                    'a': "Sever the heart's strings - free it",
                    'b': "Complete the doll - add your hair to it",
                    'c': "Smash your face-doll - destroy it",
                    'd': "Wind the music box - hear its song"
                },
                'consequences': {
                    'a': {'immediate': "The heart stops. All dolls turn to face you.", 'delayed_reveal_level': 18, 'is_wrong': True},
                    'b': {'immediate': "The doll's eyes blink. It mouths 'thank you'.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'c': {'immediate': "You feel a sharp pain in your chest. The heart screams.", 'delayed_reveal_level': 20, 'is_wrong': True},
                    'd': {'immediate': "The song is your mother's lullaby... but she never sang.", 'delayed_reveal_level': 6, 'is_wrong': True}
                }
            },
            16: {
                'description': (
                    "The walls pulse like living tissue. Veins protrude from the plaster. "
                    "When you touch them, they throb in time with your heartbeat. "
                    "A mouth forms in the wall and whispers your childhood nickname."
                ),
                'options': {
                    'a': "Answer the mouth - speak your name",
                    'b': "Cut a vein - see what flows out",
                    'c': "Press your ear to the wall - listen",
                    'd': "Run - this is too much"
                },
                'consequences': {
                    'a': {'immediate': "The walls absorb your voice. Now they sound like you.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'b': {'immediate': "Black sludge oozes out. It smells like your childhood home.", 'delayed_reveal_level': 19, 'is_wrong': True},
                    'c': {'immediate': "You hear your own voice from years ago, begging for help.", 'delayed_reveal_level': 10, 'is_wrong': True},
                    'd': {'immediate': "The corridor elongates. The mouth laughs.", 'delayed_reveal_level': 7, 'is_wrong': True}
                }
            },
            17: {
                'description': (
                    "A puppet theater where shadow plays depict your childhood memories... "
                    "with disturbing new details. The control strings lead upward into darkness. "
                    "Your shadow doesn't match your movements."
                ),
                'options': {
                    'a': "Pull the strings - take control",
                    'b': "Watch the play - see the truth",
                    'c': "Cut the strings - free yourself",
                    'd': "Step into the stage - join the shadows"
                },
                'consequences': {
                    'a': {'immediate': "The shadows resist. You feel strings around your own wrists.", 'delayed_reveal_level': 20, 'is_wrong': True},
                    'b': {'immediate': "The play shows your deepest regret. The audience weeps.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'c': {'immediate': "Something screeches above you. The theater goes dark.", 'delayed_reveal_level': 14, 'is_wrong': True},
                    'd': {'immediate': "Your shadow stays behind. It waves goodbye.", 'delayed_reveal_level': 11, 'is_wrong': True}
                }
            },
            18: {
                'description': (
                    "A hallway lined with jars of teeth. One jar contains your baby teeth. "
                    "The label reads: 'Payment rendered'. A dentist's chair sits at the end, "
                    "its drill whirring to life as you approach."
                ),
                'options': {
                    'a': "Reclaim your teeth - take them back",
                    'b': "Add a tooth - pay the price",
                    'c': "Smash the jars - reject this collection",
                    'd': "Sit in the chair - submit"
                },
                'consequences': {
                    'a': {'immediate': "The teeth chatter in your hand. They remember your gums.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'b': {'immediate': "You spit a molar into a jar. The drill purrs.", 'delayed_reveal_level': 13, 'is_wrong': True},
                    'c': {'immediate': "The shards form a grinning mouth on the floor.", 'delayed_reveal_level': 16, 'is_wrong': True},
                    'd': {'immediate': "The restraints click shut. The drill descends.", 'delayed_reveal_level': 9, 'is_wrong': True}
                }
            },

            # --- FINAL LEVELS ---
            19: {
                'description': "A mirror spanning wall to wall. Your reflection is missing. Behind you, all previous versions of yourself watch. The frame has five notches matching objects from your journey.",
                'options': {
                    'a': "Step into the mirror - embrace the void", # Correct choice for secret ending
                    'b': "Turn to face the others - confront your past",
                    'c': "Shatter the glass - break the cycle",
                    'd': "Close your eyes - surrender"
                },
                'consequences': {
                    'a': {'immediate': "The surface ripples like water. Something grabs your ankle.", 'delayed_reveal_level': None, 'is_wrong': False},
                    'b': {'immediate': "They mimic your movements... but one second delayed.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'c': {'immediate': "The shards reform mid-air. Now there are two of you.", 'delayed_reveal_level': None, 'is_wrong': True},
                    'd': {'immediate': "You feel breath on your neck.", 'delayed_reveal_level': None, 'is_wrong': True}
                }
            },

            20: {
                'description': "The final door opens by itself. The symbols pulse in time with your heartbeat.",
                'options': {}, # No options for the final decision level
                'ending': {
                    'good': "Sunlight! But as you step through, you wake in your bed... with the rusty key on your nightstand. Was it all a dream? Or just the beginning?",
                    'bad': "The void beyond the door swallows you. Hands grab you as a voice whispers: 'You shouldn't have picked up that key.' Your screams echo into oblivion.",
                    'neutral': "You exit to find yourself back at the beginning. The key lies where it was. Will you make the same choices? The cycle continues.",
                    'secret': (
                        "The mirror ripples. You fall into your childhood bed. The House whispers: "
                        "'You were never really here. We only borrowed your dreams.' "
                        "Under your pillow: a rusted key, a music box gear, a page from that book, "
                        "a doll's eye, and a lock of your hair. The memories are yours, but the echoes remain."
                    )
                }
            }
        }

    def check_secret_ending(self, past_choices):
        # A specific sequence of choices leads to the secret ending
        # (Level, Choice) pairs that must be present in the player's history
        secret_path = [(1, 'b'), (3, 'd'), (6, 'c'), (12, 'd'), (19, 'a')]
        # Convert past_choices to a set for efficient lookup
        choices_made = {(c['level'], c['choice']) for c in past_choices}
        return all(step in choices_made for step in secret_path)

    def determine_ending(self, past_choices):
        if self.check_secret_ending(past_choices):
            return 'secret'

        # Analyze choices for ending conditions
        stats = {
            'keys_taken': sum(1 for c in past_choices if (c['level'], c['choice']) in [(1,'a'), (7,'a'), (14,'a')]),
            'sanity_lost': sum(1 for c in past_choices if c.get('is_wrong', False)), # Count 'wrong' choices
            'mirror_interactions': sum(1 for c in past_choices if c['level'] in [3,12,19])
        }

        # Prioritize bad ending if too many wrong choices
        if stats['sanity_lost'] >= 8: # Increased threshold for bad ending to make it less common
            return 'bad'
        elif stats['keys_taken'] >= 2 and stats['sanity_lost'] < 4: # Require fewer wrong choices for good ending
            return 'good'
        elif stats['mirror_interactions'] >= 3:
            return 'neutral'
        else: # Default to a random ending if no specific conditions are met
            return random.choice(['good', 'bad', 'neutral'])

    def get_ending(self, ending_type):
        return self.scenarios[20]['ending'].get(ending_type, "An unexpected end.")

    def get_delayed_message(self, source_level, choice):
        # Specific messages for choices that have 'delayed_reveal_level' set
        messages = {
            1: {
                'a': "A cold sensation runs down your arm from where the key rests. It feels... alive.",
                'c': "The torchlight seems to dim around you, casting longer, more unsettling shadows.",
                'd': "That echoed voice? It's not just in the room. It's in your mind, a faint, unsettling hum."
            },
            2: {
                'a': "You feel a faint, sticky residue on your skin. The scent of rot lingers in your nose.",
                'b': "The whispers you heard earlier now seem to be forming coherent, unsettling phrases, just at the edge of your hearing.",
                'd': "A phantom pain shoots through your back where the door once stood. The bloodstained wall seems to pulse."
            },
            3: {
                'a': "Your reflection's silent plea resurfaces, a fleeting image in your mind's eye.",
                'b': "A cloying, thick sensation coats your tongue, even now. The rising liquid in the tub replays in your memory.",
                'c': "You hear a faint, distant music box chime, out of sync with your surroundings, a chilling reminder."
            },
            4: {
                'a': "The words 'NOW IT SEES YOU TOO' flash in your mind. You feel a prickling sensation on your skin, as if watched.",
                'c': "The feeling of your own handwriting on the page, the chilling realization of authorship, returns to haunt you."
            },
            5: {
                'a': "The phantom creak of chairs, the sense of unseen presences, sends a shiver down your spine.",
                'b': "The taste of that childhood meal turns metallic in your mouth. The sound of chewing seems to emanate from the very air around you.",
                'd': "The turning door handle echoes in your memory, a silent, unsettling promise of what lies ahead."
            },
            6: {
                'a': "The ghostly touch of a tiny hand, the image of an empty crib, returns to you, unnervingly real.",
                'd': "The backwards lullaby now plays a discordant melody in your mind, a persistent, unsettling tune."
            },
            7: {
                'a': "A sharp, phantom bite on your hand. The stubborn key, the whispering flower... the memory sends a jolt through you.",
                'c': "The shriek of your face-flower, the turning of the other plants... you feel their cold, accusing gaze still upon you."
            },
            8: {
                'a': "The chalk re-forming, the relentless rewriting... you feel a sense of powerlessness, a grim lesson learned.",
                'c': "Your hands feel perpetually dusty, a phantom residue of the chalk that wouldn't wash off. A constant reminder of a losing battle.",
                'd': "The board's chilling 'GOOD STUDENT' rings in your ears, a false approval that feels more like a curse."
            },
            9: {
                'a': "The cold, unnatural feel of the rose, the prick of its thorns... you feel a phantom pain, a warning unheeded.",
                'c': "The endless, circular pursuit of the music, always just out of reach, reflects a deeper, unsettling truth about this place."
            },
            10: {
                'a': "The phantom brush of fur or hair on your face, the pervasive, sickly sweet scent... the darkness of the crawlspace lingers.",
                'c': "The echoes of your own banging, magnified by unseen whispers, return to you, a chilling cacophony.",
                'd': "The glint of distant eyes, the sensation of breath on your skin... the memory of waiting in the dark is truly unsettling."
            },
            11: {
                'a': "The toys' stubborn return to their menacing positions, a defiance of your will, plays out in your mind's eye.",
                'd': "The searing heat of the door handle, the sudden trap... you feel the lingering frustration and dread of being caught."
            },
            12: {
                'a': "The chilling realization that your hands passed through the imposter, its silent pointing, leaves a cold dread in your stomach.",
                'c': "The doppelganger's silent words, the unsettling absence of your own shadow... you question your very existence here."
            },
            13: {
                'a': "The jarring unison of the clocks, the blurring of your vision... a sense of disorientation, a loss of control, returns.",
                'c': "The gears snagging your sleeve, the clock face mocking you with your age at death... a profound sense of foreboding.",
                'd': "The relentless ticking, now indistinguishable from your own accelerated heartbeat, pounds in your ears."
            },
            14: {
                'a': "The key fused to your palm, the rattling bones... the cold, dead weight of your choice still clings to you.",
                'd': "The reassembling bones, forming a towering, accusatory figure... you feel its immense, judging presence still."
            },
            15: {
                'a': "The silent turning of the dolls, the stopped heart... a chilling stillness, a profound sense of finality.",
                'c': "The sharp pain in your chest, the doll's scream echoing... you feel a deep, visceral connection to its demise."
            },
            16: {
                'b': "The black sludge, the smell of your childhood home... a sickening sensation, a violation of cherished memories.",
                'c': "Your own voice, begging for help from the wall... the memory is a raw, agonizing wound.",
                'd': "The endless corridor, the mocking laughter... you feel the futility of escape, a growing despair."
            },
            17: {
                'a': "The phantom strings around your wrists, the resistance of the shadows... a feeling of being manipulated, a loss of agency.",
                'c': "The screech from above, the sudden darkness... a deep, unsettling fear of the unknown consequences of your defiance.",
                'd': "The image of your shadow waving goodbye, a silent farewell to a part of yourself, lingers with a haunting poignancy."
            },
            18: {
                'b': "The chilling realization of spitting a molar into a jar, the purring drill... you feel the metallic taste of sacrifice.",
                'c': "The shards forming a grinning mouth on the floor... a grotesque, mocking image that haunts your vision.",
                'd': "The click of the restraints, the descending drill... a cold, clinical dread, a sense of inevitable torment."
            },
            19: {
                'b': "The unsettling delay in your reflections' movements, a constant reminder of something subtly wrong, something following you.",
                'c': "The relentless re-formation of the glass, the sudden appearance of another 'you'... a terrifying sense of self-replication and loss of identity.",
                'd': "The ghost of breath on your neck, a constant chill, a reminder of the unseen presence that lingers right behind you."
            }
        }
        return messages.get(source_level, {}).get(choice, "A forgotten shadow stirs within you...")


    def get_scenario(self, level):
        return self.scenarios.get(level, {})

game_logic = GameLogic()

# --- Flask Routes ---

@app.route('/')
def index():
    # Initialize game state in session
    session.clear() # Clear any previous session data
    session['current_level'] = 1
    session['past_choices'] = [] # Store {'level': X, 'choice': 'y', 'is_wrong': True/False}
    session['delayed_consequences_pending'] = [] # Stores {'source_level': X, 'choice': 'y', 'reveal_level': Z}
    return redirect(url_for('play_game'))

@app.route('/play', methods=['GET', 'POST'])
def play_game():
    current_level_num = session.get('current_level', 1)

    # Check if we're at the final level (Level 20)
    if current_level_num > game_logic.total_levels:
        ending_type = game_logic.determine_ending(session.get('past_choices', []))
        ending_text = game_logic.get_ending(ending_type)
        session.clear() # Clear session after game ends
        return render_template('game_over.html', message=ending_text, is_ending=True)

    current_scenario = game_logic.get_scenario(current_level_num)

    # Handle POST request (player made a choice)
    if request.method == 'POST':
        chosen_option_key = request.form.get('choice')
        if not chosen_option_key or chosen_option_key not in current_scenario.get('options', {}):
            # Invalid choice, re-render current level with an error or just ignore
            return redirect(url_for('play_game')) # Simply re-render current state

        consequence_info = current_scenario['consequences'].get(chosen_option_key)

        # Store the choice for ending determination and delayed consequences
        session['past_choices'].append({
            'level': current_level_num,
            'choice': chosen_option_key,
            'is_wrong': consequence_info.get('is_wrong', False)
        })

        # Add to pending delayed consequences if applicable
        if consequence_info.get('delayed_reveal_level') is not None:
            session['delayed_consequences_pending'].append({
                'source_level': current_level_num,
                'choice': chosen_option_key,
                'reveal_level': consequence_info['delayed_reveal_level']
            })

        # Advance to the next level
        session['current_level'] = current_level_num + 1
        return redirect(url_for('play_game'))

    # Handle GET request (display current scenario)
    if not current_scenario:
        # This shouldn't happen if levels are sequential, but as a fallback
        session.clear()
        return render_template('game_over.html', message="An unknown error occurred or you've reached an undefined path.")

    # Check for delayed messages to display at this level
    messages_to_display = []
    # Create a new list for pending consequences to avoid modifying during iteration
    newly_pending = []
    for dc in session.get('delayed_consequences_pending', []):
        if dc['reveal_level'] == current_level_num:
            message = game_logic.get_delayed_message(dc['source_level'], dc['choice'])
            if message: # Ensure there's a message to display
                messages_to_display.append(message)
        else:
            newly_pending.append(dc) # Keep it if not yet due

    session['delayed_consequences_pending'] = newly_pending # Update the session with remaining pending

    # Immediate consequence message (if any)
    immediate_message = ""
    # This assumes 'immediate' message is from the *previous* choice that led to this level.
    # To display it correctly, the immediate message would need to be passed from the POST to the GET.
    # For simplicity, we'll focus on delayed for now, or you can add a 'last_immediate_message' to session.

    # For a level with no options (like a "consequence" or "dead end" level within the main flow)
    if not current_scenario.get('options'):
        message = current_scenario.get('description', "Your path ends here.")
        session.clear() # Game over if no options
        return render_template('game_over.html', message=message, is_ending=True)

    return render_template('game.html',
                           scenario=current_scenario['description'],
                           options=current_scenario['options'],
                           level_number=current_level_num,
                           total_levels=game_logic.total_levels,
                           delayed_messages=messages_to_display,
                           immediate_message=immediate_message) # Pass immediate_message if you implement it

if __name__ == '__main__':
    # For production, use a more robust server like Gunicorn or Waitress
    app.run(debug=True) # debug=True allows for automatic reloading on code changes