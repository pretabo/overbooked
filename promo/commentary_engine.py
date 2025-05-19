"""
Commentary engine for wrestling promos.
Handles generation of promo lines and commentary based on match state and triggers.
"""

import random

# Promo line templates organized by tone, theme, and phase
PROMO_TEMPLATES = {
    "boast": {
        "legacy": {
            "opening": [
                "Let me tell you about greatness",
                "You're looking at living history right now",
                "They say legends are born, not made",
                "When you think of wrestling royalty, you think of me",
                "The history books are being written as we speak",
                "Some chase glory, others define it",
                "In an industry of pretenders, I stand alone",
                "Your heroes had one thing in common - me",
                "Let's talk about what makes a legend",
                "The air feels different when greatness enters the room",
                "There's a reason they call me the benchmark",
                "Generations will study what happens next",
                "The measuring stick just walked through that curtain",
                "Tonight you witness history in motion",
                "They say timing is everything in this business",
                "Welcome to a masterclass in excellence",
                "The blueprint for success stands before you",
                "Witness the evolution of perfection",
                "The standard bearer has arrived",
                "Every legend needs their storyteller",
                "The history of this business walks and talks",
                "Icons aren't born in comfort zones",
                "The measure of greatness stands before you",
                "Legends walk among mere mortals tonight",
                "The difference between good and great is me",
                "Welcome to the summit of excellence",
                "The pinnacle has a new definition",
                "Greatness casts a long shadow",
                "The bar rises when I enter the room",
                "Your textbook needs a new chapter",
                "The legacy of this business evolves tonight",
                "Watch closely - history unfolds",
                "The benchmark just entered the building",
                "Excellence has a new address",
                "The standard just got an upgrade",
                "Legends aren't made - they're forged",
                "The crown weighs heavy for a reason",
                "Welcome to the masterclass",
                "The definition of iconic walks and talks",
                "Your heroes had heroes - they called me boss"
            ],
            "middle": [
                "I don't just follow history - I write it",
                "You cheer for legends, you're looking at one",
                "Every era needs its icon, this one's mine",
                "My legacy isn't being written - it's being carved in stone",
                "Legends are born in moments like these",
                "History remembers the greats, it worships the legends",
                "Your heroes had posters on their walls of me",
                "I'm not in the history books - I'm writing them",
                "Each night in this ring adds to my legacy",
                "The throne room has one occupant",
                "Excellence isn't a goal, it's a requirement",
                "My shadow stretches across generations",
                "What I do in this ring rewrites the playbook",
                "The standard bearer has arrived",
                "My reputation precedes me, my legacy exceeds it",
                "Every move I make becomes tomorrow's textbook",
                "They don't build statues of critics",
                "Greatness recognizes greatness",
                "The history of this business runs through me",
                "My influence extends beyond these four corners",
                "The crown fits perfectly where it belongs",
                "Your idols studied my highlight reel",
                "The torch wasn't passed - I took it",
                "My footsteps become tomorrow's path",
                "Excellence flows through these veins",
                "The blueprint of greatness stands before you",
                "My legacy outshines your dreams",
                "Icons don't follow trends - we set them",
                "The measuring stick bends to my standards",
                "Your ceiling is my starting line",
                "Greatness isn't earned - it's embodied",
                "The history books write themselves around me",
                "My presence rewrites the definition of elite",
                "Legends bow when I enter the room",
                "The throne room has my name engraved",
                "Your best day can't touch my average",
                "My shadow stretches across eras",
                "The benchmark rises when I speak",
                "Excellence recognizes its master",
                "Your legacy ends where mine begins",
                "The standard of greatness wears my face",
                "Icons create the path others follow",
                "My influence echoes through generations",
                "The crown serves its true king",
                "Legends whisper my name in reverence"
            ],
            "ending": [
                "Remember this moment - you witnessed greatness",
                "Let my legacy be your lesson",
                "History will remember what happens next",
                "The next chapter begins right now",
                "Your children will talk about what they saw tonight",
                "This is how legends cement their status",
                "Watch closely - this is how it's done",
                "Tonight becomes tomorrow's highlight reel",
                "My legacy grows with every passing moment",
                "The history books just got another page",
                "This is what immortality looks like",
                "Remember where you were when this happened",
                "The benchmark just got raised again",
                "Witness the birth of another classic",
                "Time to add another chapter to the legend",
                "The crown finds its rightful place",
                "Greatness leaves its mark tonight",
                "Watch how legends write their story",
                "The history books need a new chapter",
                "Excellence finds its true home",
                "Your witness to greatness ends here",
                "The legacy grows stronger tonight",
                "Remember the night perfection walked",
                "Witness how icons cement their place",
                "The standard rises with my exit",
                "Glory finds its true meaning now",
                "Watch how legends take their leave",
                "The blueprint of excellence stands complete",
                "Your education in greatness concludes",
                "Witness the power of true legacy",
                "The throne room keeps its king",
                "Excellence leaves its final mark",
                "Remember who rewrote the rules",
                "The measuring stick finds new heights",
                "Greatness takes its final bow",
                "Watch how icons write their ending",
                "The legacy stands unmatched",
                "History bows to its master",
                "The crown weighs heavier now",
                "Witness the final stroke of brilliance"
            ]
        },
        "dominance": {
            "opening": [
                "Let me explain something about dominance",
                "The hierarchy in that locker room is real simple",
                "You want to talk about levels in this business",
                "The food chain in this industry is simple",
                "Allow me to demonstrate superiority",
                "The gap between us is no accident",
                "Some call it arrogance, I call it accuracy",
                "The definition of dominance just walked in",
                "There's a reason I stand where I stand",
                "The view from the top is exactly as I imagined",
                "Let's discuss the natural order of things",
                "The pecking order is about to be reinforced",
                "Time for a lesson in superiority",
                "The difference between us isn't luck",
                "When excellence speaks, you should listen",
                "Welcome to a masterclass in dominance",
                "The apex predator enters the arena",
                "Let me show you what real power looks like",
                "The food chain has a new alpha",
                "Time to establish the natural order",
                "The hierarchy needs a reminder",
                "Your education in power begins now",
                "The supreme force has arrived",
                "Witness true dominance in motion",
                "The pinnacle has a guardian",
                "Your lesson in superiority starts here",
                "The throne room welcomes its ruler",
                "Time to witness real authority",
                "The peak has an owner",
                "Your master class begins now",
                "The alpha enters the arena",
                "Witness the power hierarchy",
                "The summit has its king",
                "Time for a lesson in supremacy",
                "The dominant force arrives",
                "Your tutorial in power starts now",
                "The apex shows its face",
                "Time to demonstrate true might",
                "The mountain has its master",
                "Your schooling in strength begins"
            ],
            "middle": [
                "Nobody in that locker room can touch me",
                "I'm not just better - I'm in a different league",
                "You're all living in my world now",
                "There's the best, and then there's me",
                "I don't compete - I dominate",
                "The gap between us? It's called greatness",
                "You're looking at wrestling perfection",
                "I don't chase greatness, it follows me",
                "Your best day can't touch my worst",
                "The throne isn't vacant, it's occupied",
                "Excellence isn't a moment, it's a lifestyle",
                "The difference between us is called talent",
                "My warm-up is your finish line",
                "I don't set the bar, I am the bar",
                "Success follows excellence",
                "Your ceiling is my starting point",
                "The standard isn't high enough until I raise it",
                "Mediocrity fears what I represent",
                "I don't hope to win, I expect to dominate",
                "The game changes when I'm in it",
                "Your best effort is my warm-up routine",
                "The gap between us grows with every breath",
                "I don't just raise the bar - I am the bar",
                "Your peak performance is my starting point",
                "The throne room has one occupant - me",
                "Excellence bows when I enter the room",
                "Your greatest achievement is my daily standard",
                "The difference between us can't be measured",
                "I don't compete in your league - I own it",
                "Your maximum effort makes me yawn",
                "The apex predator shows no mercy",
                "Dominance flows through my veins",
                "Your struggle amuses the master",
                "The food chain bows to its king",
                "Supremacy recognizes its champion",
                "Your limits define my warmup",
                "The alpha shows its dominance",
                "Power recognizes true strength",
                "Your best shot bounces off greatness",
                "The mountain bows to its conqueror",
                "Excellence finds its true form",
                "Your ceiling can't touch my floor",
                "The hierarchy knows its master",
                "Strength finds its pure expression",
                "Your peak meets my valley"
            ],
            "ending": [
                "Class dismissed - that's how it's done",
                "Consider this your reality check",
                "The gap between us just got wider",
                "Remember who sits at the top",
                "That's what real power looks like",
                "Witness what dominance truly means",
                "The lesson ends here",
                "The difference is clear for all to see",
                "Your best just met its master",
                "The hierarchy remains unchanged",
                "Excellence just made its point",
                "The standard remains unmatched",
                "Superiority speaks for itself",
                "The throne room remains occupied",
                "The king stays the king",
                "The alpha stands unchallenged",
                "Dominance finds its true expression",
                "Witness the power gap widen",
                "The mountain stands unconquered",
                "Excellence shows its final form",
                "Your education in power concludes",
                "The apex predator claims victory",
                "Witness true supremacy manifest",
                "The hierarchy stands reinforced",
                "Power shows its ultimate form",
                "Your lesson in strength concludes",
                "The dominant force prevails",
                "Watch how kings take their leave",
                "The summit remains untouchable",
                "Greatness claims its territory",
                "The alpha makes its mark",
                "Dominance writes its final chapter",
                "Witness how champions exit",
                "The peak stays unconquered",
                "Power leaves its lasting mark",
                "The throne room keeps its master",
                "Supremacy shows its true face",
                "Watch how legends claim victory",
                "The mountain stays unmoved",
                "Excellence takes its final bow"
            ]
        }
    },
    "insult": {
        "betrayal": {
            "opening": [
                "Let's talk about loyalty for a minute",
                "The snake reveals its true colors",
                "Trust is such a fragile thing",
                "Friendship means nothing to people like you",
                "Some debts demand payment",
                "Betrayal has a funny way of coming full circle",
                "Time to address the elephant in the room",
                "Let's discuss your recent choices",
                "The truth about loyalty is simple",
                "Some wounds cut deeper than others",
                "Karma keeps a perfect record",
                "Let's talk about consequences",
                "The price of betrayal comes due",
                "Time to settle some accounts",
                "Your actions speak volumes about your character",
                "The mask finally falls away",
                "Time to expose the real you",
                "Let's discuss the meaning of trust",
                "The traitor shows their face",
                "A snake sheds its skin tonight",
                "The truth stands revealed at last",
                "Time to unmask the deceiver",
                "Let's talk about broken bonds",
                "The betrayer steps into light",
                "Your true nature comes forward",
                "Time to face what you've done",
                "The debt collector comes calling",
                "Let's discuss your treachery",
                "The price of disloyalty comes due",
                "Your mask slips away tonight",
                "Time to confront your choices",
                "The veil of deception lifts",
                "Let's examine your betrayal",
                "The cost of treachery awaits",
                "Your facade crumbles tonight",
                "Time to face the music",
                "The truth demands its due",
                "Let's settle this account",
                "The day of reckoning arrives",
                "Your deception ends tonight"
            ],
            "middle": [
                "You turned your back on me? Big mistake",
                "Loyalty means nothing to a snake like you",
                "Friends? You don't deserve that word",
                "Your true colors are showing, and they're yellow",
                "Betrayal has a price, you'll pay in full",
                "Trust is earned, betrayal is paid for",
                "You stabbed me in the back? I'm coming for your throat",
                "Every snake eventually gets what's coming",
                "Your betrayal writes checks your body can't cash",
                "The knife in my back has your fingerprints",
                "Judas has nothing on you",
                "Loyalty was never in your vocabulary",
                "Your word means less than nothing",
                "The mask you wore fooled everyone",
                "Trust is earned, respect is given, loyalty is proven",
                "Your actions have consequences",
                "The debt collector has come calling",
                "Time to pay what you owe",
                "The price of betrayal comes steep",
                "Your treachery knows no bounds",
                "Each lie you told digs your grave deeper",
                "The snake pit welcomes its newest resident",
                "Your deception writes its own punishment",
                "The price of treachery grows steeper",
                "Every betrayal leaves its mark",
                "The debt of disloyalty compounds daily",
                "Your false face fools no one now",
                "The cost of your choices comes due",
                "Each lie strengthens my resolve",
                "The truth cuts deeper than your knife",
                "Your betrayal fuels my vengeance",
                "The price of treachery doubles tonight",
                "Every snake meets its charmer",
                "The cost of deception grows higher",
                "Your lies build my strength",
                "The debt collector never forgets",
                "Each betrayal sharpens my focus",
                "The price of disloyalty multiplies",
                "Your treachery feeds my fire",
                "The cost of betrayal accumulates",
                "Every snake sheds its skin",
                "The price of deception compounds",
                "Your lies strengthen my purpose",
                "The debt of betrayal grows",
                "Each treachery marks your fate"
            ],
            "ending": [
                "The bill comes due tonight",
                "Time to face the consequences",
                "Your judgment day arrives",
                "The price of betrayal gets paid",
                "Watch your back - I learned from the best",
                "Payback hits harder than karma",
                "The debt collector stands ready",
                "Your time of reckoning approaches",
                "Justice wears my face tonight",
                "The snake pit awaits its maker",
                "Vengeance comes with interest",
                "The betrayer becomes the betrayed",
                "Your chickens come home to roost",
                "The scales of justice tip tonight",
                "Retribution wears my name",
                "The price of treachery comes due",
                "Your debt gets settled tonight",
                "Watch how karma collects its due",
                "The betrayer meets their fate",
                "Time for the final accounting",
                "Your judgment finds its mark",
                "The debt collector claims their due",
                "Watch your empire crumble",
                "The price of deception comes full circle",
                "Your treachery meets its match",
                "Time for the final reckoning",
                "The snake meets its mongoose",
                "Watch your world unravel",
                "The cost of betrayal comes home",
                "Your lies meet their truth",
                "Time for the ultimate price",
                "The deceiver faces reality",
                "Watch your facade shatter",
                "The debt finds its collector",
                "Your treachery meets justice",
                "Time for the final payment",
                "The snake faces its charmer",
                "Watch your choices catch up",
                "The price of disloyalty arrives",
                "Your deception meets its end"
            ]
        },
        "power": {
            "opening": [
                "Let me show you what real power looks like",
                "You call that strength? Let me educate you",
                "Time for a lesson in real power",
                "The definition of strength stands before you",
                "Allow me to demonstrate true power",
                "Your so-called strength amuses me",
                "The measure of power is simple",
                "Let's talk about what makes someone strong",
                "Your version of power needs correction",
                "Time to separate pretenders from contenders",
                "The strong survive, the weak perish",
                "Power has a new definition",
                "Strength isn't what you think it is",
                "The weak fear what I represent",
                "True power demands respect",
                "Your strength is an illusion",
                "Let me show you real might",
                "Time to expose your weakness",
                "Your power is a mere shadow",
                "Watch true strength manifest",
                "The weak pretend at power",
                "Let me demonstrate real force",
                "Time to reveal true strength",
                "Your might is just pretense",
                "Witness authentic power",
                "The strong expose the weak",
                "Let me unveil true might",
                "Time to show real dominance",
                "Your strength lacks substance",
                "Watch genuine power unfold",
                "The mighty crush the meek",
                "Let me display true force",
                "Time to prove real strength",
                "Your power rings hollow",
                "Witness undeniable might",
                "The strong devour the weak",
                "Let me exhibit true power",
                "Time to showcase real force",
                "Your strength falls short",
                "Watch absolute power manifest"
            ],
            "middle": [
                "You're not even in my weight class",
                "They call that power? That's cute",
                "You couldn't hang with me on my worst day",
                "All that training, and you're still this weak",
                "Your best punch? I call that a warm-up",
                "That's not power, let me show you power",
                "You bring a spark, I bring a storm",
                "Your strength? It's an insult to the word",
                "Power isn't given, it's taken",
                "Your definition of strong needs work",
                "Real power stands before you",
                "Strength has a new standard",
                "Your might is my amusement",
                "True power knows no equal",
                "The gap in our power is laughable",
                "Your strength is my warm-up",
                "Power recognizes weakness",
                "The strong eat, the weak starve",
                "Might makes right, and I make might",
                "Your power is my plaything",
                "Your strength makes me laugh",
                "Call that power? How adorable",
                "You're playing in the kiddie pool",
                "That's not strength, that's wishful thinking",
                "Your might is my amusement",
                "Real force shows no mercy",
                "You bring rain, I bring hurricanes",
                "Your power is a joke to me",
                "True strength shows no equal",
                "The weak imitate the strong",
                "Your might crumbles before me",
                "Real power knows no bounds",
                "You're a pebble to my mountain",
                "That force? Barely a breeze",
                "Your strength wilts before mine",
                "True might stands revealed",
                "You're a spark to my inferno",
                "That power? Child's play",
                "Your force bends to my will",
                "Real strength dominates all",
                "You're a wave to my tsunami",
                "That might? Just a whisper",
                "Your power serves my purpose",
                "True force commands respect",
                "You're nothing to my everything"
            ],
            "ending": [
                "Class dismissed - weakness exposed",
                "Power speaks louder than words",
                "Strength shows itself tonight",
                "The weak fall, the strong remain",
                "True power stands revealed",
                "Witness real strength in action",
                "The gap in our power shows clear",
                "Your weakness becomes evident",
                "Power has a new name tonight",
                "The strong survive what comes next",
                "Strength finds its true measure",
                "The weak fade, the strong shine",
                "Power speaks its final word",
                "Your weakness seals your fate",
                "True might prevails tonight",
                "The lesson in power concludes",
                "Witness true strength triumph",
                "The weak learn their place",
                "Power shows its true face",
                "Your might falls short again",
                "The strong stand victorious",
                "Watch real power prevail",
                "The gap becomes a chasm",
                "Your strength proves lacking",
                "True force claims victory",
                "The mighty stand alone",
                "Witness power incarnate",
                "The weak fade to nothing",
                "Strength claims its throne",
                "Your might meets its master",
                "The powerful reign supreme",
                "Watch true strength conquer",
                "The divide grows wider",
                "Your power finds its limit",
                "Real might stands triumphant",
                "The strong write history",
                "Witness true dominance",
                "The weak accept defeat",
                "Power claims its crown",
                "Your strength bows to mine"
            ]
        }
    },
    "callout": {
        "comeback": {
            "opening": [
                "They say comebacks are impossible",
                "The rumors of my demise were premature",
                "Time to set the record straight",
                "Let's talk about resurrection",
                "They tried to write me off",
                "The story isn't over yet",
                "Reports of my downfall were exaggerated",
                "The phoenix rises again",
                "Let me tell you about survival",
                "The comeback trail starts here",
                "Time to rewrite the narrative",
                "The end? This is just the beginning",
                "They thought the book was closed",
                "The story continues tonight",
                "Chapter one of the comeback starts now",
                "They counted me out too soon",
                "The final chapter isn't written",
                "Let me show you what resilience means",
                "They buried me before I was dead",
                "The comeback kid steps up",
                "Time to prove them all wrong",
                "Watch resurrection in action",
                "They forgot who they're dealing with",
                "The story takes a new turn",
                "Let me remind you who I am",
                "They wrote the eulogy too early",
                "The phoenix never stays down",
                "Time to shock the world",
                "Watch how legends return",
                "The story finds new life",
                "Let me show you true resilience",
                "They celebrated too soon",
                "The comeback tour begins now",
                "Time to rewrite history",
                "Watch the impossible unfold",
                "The story demands its due",
                "Let me demonstrate perseverance",
                "They underestimated my resolve",
                "The return starts tonight",
                "Time to prove my worth"
            ],
            "middle": [
                "You thought I was finished? Think again",
                "Count me out at your own risk",
                "The story's not over until I say it is",
                "You can't keep a legend down",
                "Every setback just fuels my comeback",
                "They tried to bury me, they forgot I was a seed",
                "Down but never out, that's my story",
                "The greatest comebacks start with the biggest doubts",
                "What doesn't kill me makes me stronger",
                "The comeback is always stronger than the setback",
                "Rising from the ashes is what I do",
                "Each fall makes the rise more impressive",
                "The climb back up just makes me stronger",
                "Adversity builds character",
                "The harder the fall, the higher the bounce",
                "You can't break what bends",
                "The comeback is just beginning",
                "Watch me rise again",
                "Every setback sets up a comeback",
                "The rise after the fall defines us",
                "Your doubt fuels my determination",
                "Each obstacle strengthens my resolve",
                "The naysayers power my return",
                "Your mockery feeds my motivation",
                "Every critic adds to my strength",
                "The doubters drive my comeback",
                "Your laughter ignites my fire",
                "Each setback sharpens my focus",
                "The haters inspire my rise",
                "Your disbelief powers my return",
                "Every obstacle marks my path",
                "The critics cement my legacy",
                "Your scorn fuels my triumph",
                "Each fall precedes a rise",
                "The mockers motivate my return",
                "Your doubt strengthens my will",
                "Every setback builds my story",
                "The critics write my legend",
                "Your disbelief marks my ascent",
                "Each obstacle proves my worth",
                "The doubters fuel my fire",
                "Your mockery shapes my victory",
                "Each fall highlights my rise",
                "The haters script my comeback",
                "Your scorn defines my triumph"
            ],
            "ending": [
                "The comeback story writes itself tonight",
                "Watch the phoenix rise again",
                "The resurrection completes itself here",
                "Witness the return in full force",
                "The comeback kid strikes again",
                "From the ashes to the stars",
                "The rise continues unabated",
                "Victory tastes sweeter after defeat",
                "The return journey ends in triumph",
                "Watch how high I bounce back",
                "The story of redemption writes itself",
                "From setback to comeback complete",
                "The rise back to glory culminates",
                "Witness the return to form",
                "The comeback trail ends in victory",
                "The resurrection stands complete",
                "Watch legends rise again",
                "The return reaches its peak",
                "Witness triumph over adversity",
                "The comeback finds its mark",
                "From the ashes rises glory",
                "Watch history rewrite itself",
                "The return claims its prize",
                "Witness resilience personified",
                "The comeback reaches its summit",
                "From defeat springs victory",
                "Watch determination prevail",
                "The return achieves its goal",
                "Witness perseverance rewarded",
                "The comeback claims its crown",
                "From darkness comes light",
                "Watch the impossible manifest",
                "The return finds its glory",
                "Witness resolve triumphant",
                "The comeback writes its ending",
                "From doubt springs certainty",
                "Watch legends reclaim their throne",
                "The return finds its home",
                "Witness destiny fulfilled",
                "The comeback completes its arc"
            ]
        },
        "legacy": {
            "opening": [
                "Let's write some history together",
                "Time to make this moment memorable",
                "Your chance at immortality awaits",
                "Legends get made in moments like these",
                "The history books are watching",
                "Your opportunity knocks right now",
                "Time to see what you're made of",
                "The moment of truth arrives",
                "Your legacy hangs in the balance",
                "Destiny calls your name",
                "The spotlight shines bright tonight",
                "Your defining moment approaches",
                "Time to prove your worth",
                "The stage is set for greatness",
                "Your chance at glory stands before you",
                "Let's test your legendary status",
                "Time to prove your place in history",
                "Your immortality awaits its proof",
                "The books write themselves tonight",
                "Your moment of truth beckons",
                "Time to show your legendary worth",
                "The annals of history watch closely",
                "Your chance at greatness arrives",
                "Let's measure your iconic status",
                "Time to prove your legendary claim",
                "The history makers gather tonight",
                "Your legacy seeks its proof",
                "Let's test your claim to fame",
                "Time to show your historic worth",
                "The legends gather to witness",
                "Your greatness faces its trial",
                "Let's write your chapter tonight",
                "Time to prove your iconic status",
                "The history books await your tale",
                "Your legend seeks its truth",
                "Let's measure your timeless worth",
                "Time to show your lasting value",
                "The stage awaits its star",
                "Your story seeks its proof",
                "Let's write history together"
            ],
            "middle": [
                "Face me if you dare to make history",
                "Let's see if you belong in my league",
                "Time to prove why they'll remember your name",
                "Show me what future legends are made of",
                "Your legacy dies where mine begins",
                "History's calling, can you answer",
                "Legends aren't born in safety",
                "Your chapter ends where my saga begins",
                "Greatness tests itself tonight",
                "Show me what you're made of",
                "Your moment of truth arrives",
                "Prove your worth to the world",
                "Let's see what you've got",
                "Your legacy hangs by a thread",
                "Show me why they should remember you",
                "The proving ground awaits",
                "Your reputation stands trial",
                "Time to back up those words",
                "Put up or shut up time",
                "Let's test your metal",
                "Show me your claim to greatness",
                "The history books watch closely",
                "Your legend meets its measure",
                "Time to prove your worth",
                "Let's see your iconic status",
                "The annals await your proof",
                "Your legacy faces judgment",
                "Show me your timeless value",
                "The records demand evidence",
                "Your greatness seeks validation",
                "Time to show your lasting worth",
                "Let's witness your legendary claim",
                "The books await your story",
                "Your immortality stands trial",
                "Show me your historic merit",
                "The ages demand their proof",
                "Your legend seeks its truth",
                "Time to demonstrate your worth",
                "Let's see your eternal value",
                "The chronicles await your tale",
                "Your greatness meets its test",
                "Show me your timeless merit",
                "The history makers watch closely",
                "Your legacy seeks its proof",
                "Time to validate your claim"
            ],
            "ending": [
                "History judges us both tonight",
                "Legacy writes itself in blood",
                "Your story ends where mine continues",
                "Time reveals all truths",
                "The legend grows tonight",
                "Your chapter closes here",
                "Witness what happens next",
                "The future unfolds now",
                "Your legacy meets its match",
                "History has its eyes on us",
                "The saga continues through me",
                "Your story finds its end",
                "Time tells all tales",
                "The books write themselves tonight",
                "Watch how legends get made",
                "The annals record their verdict",
                "History carves its judgment",
                "Your legacy meets its measure",
                "Time stamps its final mark",
                "The legend claims its throne",
                "Your chapter finds its close",
                "Witness greatness manifest",
                "The future writes its path",
                "Your story meets its end",
                "History claims its truth",
                "The saga finds its voice",
                "Your tale reaches its close",
                "Time marks its chosen one",
                "The books claim their hero",
                "Watch legends crown their king",
                "The ages write their truth",
                "History names its champion",
                "Your legacy finds its place",
                "Time chooses its victor",
                "The legend claims its prize",
                "Your story meets its fate",
                "Witness history\'s choice",
                "The future names its heir",
                "Your tale finds its end",
                "The chronicles choose their champion"
            ]
        }
    }
}

# Quality-based commentary pools
QUALITY_COMMENTS = {
    'perfect': [
        'Absolutely perfect execution',
        'A flawless display of skill',
        'They have just delivered a career highlight',
        'This might be remembered for years',
        'The crowd is on their feet after that',
        'That was textbook perfection',
        'Pure wrestling artistry',
        'That\'s how legends are made',
        'A masterclass in mic work',
        'They\'re writing history with every word',
        'The crowd is absolutely electrified',
        'That\'s what perfection sounds like',
        'A moment that will be talked about for years',
        'They\'ve captured lightning in a bottle',
        'That\'s how you cement a legacy'
    ],
    'excellent': [
        'That was outstanding',
        'The timing and precision were impeccable',
        'A beautifully executed move',
        'They are putting on a clinic out there',
        'That hit exactly as intended',
        'Momentum is clearly theirs right now',
        'They\'re in complete control',
        'The crowd is hanging on every word',
        'That\'s how you make a statement',
        'They\'re showing why they\'re at the top',
        'A brilliant display of charisma',
        'They\'ve got the crowd in the palm of their hand',
        'That\'s championship-caliber work',
        'They\'re proving why they\'re the best',
        'The intensity is off the charts'
    ],
    'good': [
        'Nicely delivered',
        'Solid technique and timing',
        'That was well executed',
        'They are keeping the pressure up',
        'Good control on that one',
        'Steady performance so far',
        'They\'re finding their rhythm',
        'The crowd is getting behind them',
        'That\'s how you build momentum',
        'They\'re making it count',
        'Strong words, stronger delivery',
        'They\'re making their point clear',
        'The intensity is building',
        'They\'re hitting their stride',
        'That\'s how you keep control'
    ],
    'neutral': [
        'That keeps the pace steady',
        'An even exchange there',
        'Nothing flashy, but it did the job',
        'They are holding their ground',
        'Consistent work, if not spectacular',
        'Maintaining the tempo',
        'The crowd is staying engaged',
        'They\'re keeping it together',
        'Not their best, but not their worst',
        'They\'re staying in the game',
        'The momentum could swing either way',
        'They\'re treading water',
        'The intensity remains steady',
        'They\'re playing it safe',
        'The crowd is waiting for more'
    ],
    'bad': [
        'A little off the mark',
        'They seemed uncertain in that moment',
        'The execution was lacking',
        'They are starting to lose their footing',
        'That did not go as planned',
        'Crowd energy is starting to dip',
        'They\'re losing their grip',
        'The momentum is slipping away',
        'That could come back to haunt them',
        'The crowd is getting restless',
        'They\'re starting to stumble',
        'The pressure might be getting to them',
        'That\'s not what they needed',
        'They\'re falling out of rhythm',
        'The confidence is wavering'
    ],
    'terrible': [
        'A clear misstep',
        'They completely lost control there',
        'No connection at all',
        'They are on the ropes after that',
        'That was painful to watch',
        'Momentum slipping fast',
        'Everything\'s falling apart',
        'The crowd is turning on them',
        'This is going downhill fast',
        'They\'ve lost all direction',
        'Nothing is working for them',
        'The wheels are coming off',
        'This is hard to watch',
        'They\'re drowning out there',
        'It\'s all unraveling'
    ],
    'flop': [
        'That was a disaster',
        'The crowd is turning cold',
        'They have lost all rhythm',
        'Confidence is draining fast',
        'Boos are starting to ring out',
        'A total breakdown in delivery',
        'This is an absolute trainwreck',
        'They\'ve completely lost the plot',
        'The crowd is turning hostile',
        'Everything has fallen apart',
        'This is career-damaging territory',
        'They\'ve hit rock bottom',
        'The crowd has had enough',
        'This might haunt their career',
        'A complete and utter collapse'
    ]
}

# Special trigger commentary variations
SPECIAL_TRIGGER_COMMENTS = {
    'cash_in': [
        "🌟 MOMENTUM CASH-IN! A game-changing tactical decision",
        "🌟 They're cashing in their momentum at the perfect moment",
        "🌟 Strategic brilliance - converting momentum into raw confidence",
        "🌟 They're going all in - this could be the turning point",
        "🌟 A calculated risk that could change everything"
    ],
    'underdog_strike': [
        "They might just shock everyone",
        "The underdog is showing their teeth",
        "Don't count them out just yet",
        "They're defying the odds",
        "Sometimes heart beats momentum"
    ],
    'fumble_clutch': [
        "They dropped the ball at the worst moment",
        "A devastating mistake at the crucial moment",
        "They've stumbled at the finish line",
        "All that momentum, wasted in an instant",
        "The pressure got to them right at the end"
    ],
    'out_of_nowhere': [
        "No one saw that line coming",
        "Where did THAT come from",
        "A flash of brilliance from nowhere",
        "Against all odds, they've struck gold",
        "Sometimes desperation breeds perfection"
    ],
    'collapse_spiral': [
        "They're spiraling and fast",
        "Everything's falling apart for them",
        "They can't seem to stop the bleeding",
        "It's going from bad to worse",
        "They're in a dangerous downward spiral"
    ],
    'confidence_peak': [
        "They're running on pure belief right now",
        "Confidence has become unstoppable force",
        "They're in a zone few wrestlers ever reach",
        "This is what peak performance looks like",
        "They're transcending normal limits"
    ],
    'momentum_takeover': [
        "They're steamrolling now",
        "This is complete and utter dominance",
        "They're an unstoppable force right now",
        "The momentum is overwhelming",
        "Nothing can stop them in this state"
    ],
    'early_surprise': [
        "What an opening shot",
        "They've set the bar impossibly high",
        "That's how you start with a bang",
        "They're making a statement right out of the gate",
        "An explosive start that will be hard to top"
    ],
    'late_recovery': [
        "That could redeem the whole promo",
        "A strong finish can erase all mistakes",
        "They're closing on a high note",
        "That's how you stick the landing",
        "Finishing strong when it matters most"
    ],
    'wasted_opportunity': [
        "A total collapse under pressure",
        "They've crumbled at the worst moment",
        "All that momentum, gone in an instant",
        "The pressure proved too much to handle",
        "A catastrophic failure at the peak"
    ],
    'ignition_point': [
        "They've found their rhythm now",
        "They're hitting their stride",
        "The momentum is building with every word",
        "They're getting stronger by the moment",
        "Watch out - they're catching fire"
    ],
    'icy_opening': [
        "That's not how you want to start",
        "A disastrous opening that could set the tone",
        "They're digging themselves an early hole",
        "That's going to be hard to recover from",
        "The worst possible way to begin"
    ],
    'mic_drop': [
        "They couldn't have ended stronger",
        "That's how you write the final chapter",
        "A perfect exclamation point",
        "They saved the best for last",
        "An ending that will be remembered"
    ]
}

# Context commentary variations
CONTEXT_COMMENTS = {
    'momentum': {
        'dominant': [
            'They are completely dominating',
            'They\'re in a league of their own',
            'This is total supremacy',
            'They\'re unstoppable right now',
            'Pure dominance on display'
        ],
        'strong': [
            'They are on fire',
            'The momentum is explosive',
            'They\'re in complete control',
            'Nothing can stop them now',
            'They\'re reaching new heights'
        ],
        'weak': [
            'They need to build some momentum',
            'They\'re fighting uphill',
            'The struggle is real',
            'They\'re searching for answers',
            'Nothing seems to be working'
        ]
    },
    'confidence': {
        'high': [
            'Their confidence is sky-high',
            'They believe they\'re untouchable',
            'Pure swagger on display',
            'They\'re radiating confidence',
            'Their self-belief is unshakeable'
        ],
        'low': [
            'Their confidence is clearly shaken',
            'Doubt is creeping in',
            'Their swagger is gone',
            'The pressure is getting to them',
            'They\'re second-guessing everything'
        ]
    }
}

# Phase-specific commentary variations
PHASE_COMMENTS = {
    'beginning': {
        'perfect': [
            'A stunning way to open',
            'They\'ve set an incredible tone',
            'The crowd is hooked from the first word',
            'That\'s how you grab attention',
            'Opening with pure electricity'
        ],
        'good': [
            'A solid foundation to build on',
            'They\'ve got the crowd\'s attention',
            'Starting with confidence',
            'Setting a good pace early',
            'A promising beginning'
        ],
        'bad': [
            'A shaky start to overcome',
            'Not the opening they wanted',
            'They\'ll need to recover from this',
            'Early nerves showing through',
            'The crowd expected more from the start'
        ]
    },
    'middle': {
        'perfect': [
            'They\'re hitting their stride perfectly',
            'The momentum is building beautifully',
            'Every word is landing just right',
            'They\'ve found their perfect rhythm',
            'The energy is peaking at just the right time'
        ],
        'good': [
            'Keeping the energy flowing',
            'Building on their momentum',
            'The story is coming together',
            'They\'re maintaining good control',
            'The crowd is staying invested'
        ],
        'bad': [
            'Losing the thread here',
            'The momentum is slipping',
            'They\'re struggling to maintain focus',
            'The crowd\'s interest is wavering',
            'They need to turn this around'
        ]
    },
    'end': {
        'perfect': [
            'A legendary finish',
            'They couldn\'t have ended it better',
            'The perfect exclamation point',
            'That\'s how you close a promo',
            'An ending worthy of the history books'
        ],
        'good': [
            'Bringing it home strong',
            'A solid finish to the promo',
            'They\'re landing the ending',
            'The crowd will remember this',
            'Closing on a high note'
        ],
        'bad': [
            'Stumbling at the finish line',
            'Not the ending they needed',
            'The crowd\'s energy is fading fast',
            'They\'re losing it at the crucial moment',
            'A disappointing way to close'
        ]
    }
}

# Add at the top with other templates

INTRO_TEMPLATES = {
    'boast': {
        'legacy': [
            'The arena falls silent as the lights dim, the stage set for a legend to speak their truth',
            'With an aura of greatness surrounding them, they step into the spotlight to cement their legacy',
            'The crowd buzzes with anticipation as one of wrestling\'s finest prepares to address their legacy'
        ],
        'dominance': [
            'The atmosphere crackles with intensity as a dominant force takes center stage',
            'An imposing presence commands attention as they step forward to assert their dominance',
            'The crowd holds its breath, knowing they\'re about to witness a display of pure dominance'
        ]
    },
    'insult': {
        'betrayal': [
            'Tension fills the air as scores are about to be settled',
            'The crowd erupts as someone steps forward to address a bitter betrayal',
            'With vengeance in their eyes, they grab the microphone to confront their betrayer'
        ],
        'power': [
            'The atmosphere grows heavy with anticipation of the verbal warfare about to unfold',
            'A challenge to power echoes through the arena as someone steps forward',
            'The crowd stirs restlessly, sensing the impending clash of titans'
        ]
    },
    'callout': {
        'comeback': [
            'The familiar music hits and the crowd erupts, knowing redemption is at hand',
            'A moment of reckoning arrives as someone returns to settle old scores',
            'The arena buzzes with electricity as the time for comebacks draws near'
        ],
        'legacy': [
            'History hangs in the balance as a challenger steps forward to make their mark',
            'The crowd rises to their feet, knowing they\'re about to witness a defining moment',
            'With determination in their eyes, they step forward to challenge greatness itself'
        ]
    }
}

SUMMARY_TEMPLATES = {
    'perfect': [
        'A masterclass in promo delivery that will be remembered for years to come',
        'An absolutely electric performance that had the crowd hanging on every word',
        'A defining moment that showcases exactly why they\'re at the top of their game'
    ],
    'excellent': [
        'A powerful promo that hit all the right notes and left its mark',
        'An impressive display of mic skills that got the message across perfectly',
        'A memorable performance that accomplished everything it set out to do'
    ],
    'good': [
        'A solid promo that achieved its goals and kept the crowd engaged',
        'A well-executed performance that maintained momentum throughout',
        'A respectable showing that got the point across effectively'
    ],
    'neutral': [
        'A middle-of-the-road promo that had its moments but didn\'t quite soar',
        'An adequate performance that neither impressed nor disappointed',
        'A forgettable promo that served its purpose but nothing more'
    ],
    'bad': [
        'A disappointing promo that failed to connect with the audience',
        'A lackluster performance that missed its mark',
        'A forgettable showing that left much to be desired'
    ],
    'terrible': [
        'A promo to forget, with little to no redeeming qualities',
        'A complete misfire that lost the crowd entirely',
        'A performance that fell flat in every conceivable way'
    ],
    'flop': [
        'An absolute disaster that will be remembered for all the wrong reasons',
        'A catastrophic showing that damaged their credibility',
        'A complete meltdown that left the crowd in stunned silence'
    ]
}

def get_promo_line(tone, theme, phase='middle'):
    """Get a random promo line for the given tone, theme, and phase.
    
    Args:
        tone (str): The tone of the promo (boast, insult, callout)
        theme (str): The theme of the promo (legacy, dominance, betrayal, etc.)
        phase (str): The phase of the promo (opening, middle, ending)
        
    Returns:
        str: A random promo line matching the criteria
    """
    # Normalize inputs
    tone = tone.lower() if isinstance(tone, str) else 'boast'
    theme = theme.lower() if isinstance(theme, str) else 'legacy'
    phase = phase.lower() if isinstance(phase, str) else 'middle'
    
    # Validate phase is one of the allowed values
    if phase not in ['opening', 'middle', 'ending']:
        phase = 'middle'
    
    # Check if we have a valid tone
    if tone not in PROMO_TEMPLATES:
        print(f"Warning: Invalid tone '{tone}', defaulting to 'boast'")
        tone = 'boast'
        
    # Check if we have a valid theme for this tone
    if theme not in PROMO_TEMPLATES[tone]:
        # Try to find a valid theme for this tone
        valid_theme = list(PROMO_TEMPLATES[tone].keys())[0]
        print(f"Warning: Invalid theme '{theme}' for tone '{tone}', defaulting to '{valid_theme}'")
        theme = valid_theme
    
    # At this point we should have valid tone/theme/phase combinations
    try:
        return random.choice(PROMO_TEMPLATES[tone][theme][phase])
    except (KeyError, IndexError) as e:
        print(f"Error getting promo line: tone={tone}, theme={theme}, phase={phase}")
        return "..."  # Default fallback

def get_quality_comment(quality):
    """Get a random commentary line for the given quality level."""
    return random.choice(QUALITY_COMMENTS.get(quality, ['...']))

def get_special_trigger_comment(trigger):
    """Get a random special trigger commentary line."""
    return random.choice(SPECIAL_TRIGGER_COMMENTS.get(trigger, []))

def get_context_comment(context_type, level):
    """Get a random contextual commentary line."""
    if context_type in CONTEXT_COMMENTS and level in CONTEXT_COMMENTS[context_type]:
        return random.choice(CONTEXT_COMMENTS[context_type][level])
    return ""

def get_cash_in_commentary(momentum_spent, confidence_boost):
    """Generate commentary for a momentum cash-in."""
    return random.choice(SPECIAL_TRIGGER_COMMENTS['cash_in'])  # Return just the comment without the stats

def get_intro_line(tone, theme):
    """Get a random intro line for the given tone and theme."""
    tone = tone.lower() if isinstance(tone, str) else 'boast'
    theme = theme.lower() if isinstance(theme, str) else 'legacy'
    
    try:
        return random.choice(INTRO_TEMPLATES[tone][theme])
    except (KeyError, IndexError):
        return "The stage is set as another chapter in wrestling history begins to unfold"

def get_summary_line(final_quality):
    """Get a random summary line based on the overall quality of the promo."""
    try:
        return random.choice(SUMMARY_TEMPLATES[final_quality])
    except (KeyError, IndexError):
        return "And so ends another chapter in the ongoing saga"

def generate_commentary(beat):
    """Generate promo and commentary lines based on beat attributes.
    
    Args:
        beat (dict): Beat data containing quality, momentum, confidence, tone, theme, etc.
        
    Returns:
        dict: Contains promo_line and commentary_line
    """
    # Get base values
    quality = beat.get('line_quality', 'neutral')
    momentum = beat.get('momentum', 0)
    confidence = beat.get('confidence', 50)
    tone = beat.get('tone', 'boast')
    theme = beat.get('theme', 'legacy')
    phase = beat.get('phase', 'middle')
    
    # Map phases for commentary
    phase_map = {
        'beginning': 'beginning',
        'opening': 'beginning',
        'middle': 'middle',
        'end': 'end',
        'ending': 'end'
    }
    commentary_phase = phase_map.get(phase, 'middle')
    
    # Generate intro line if this is the first beat
    if beat.get('is_first_beat', False):
        intro_line = get_intro_line(tone, theme)
        return {
            "promo_line": intro_line,
            "is_intro": True,
            "commentary_line": "",
            "score": beat.get('score', 0),
            "momentum": momentum,
            "confidence": confidence
        }
    
    # Generate summary line if this is the last beat
    if beat.get('is_last_beat', False):
        final_quality = beat.get('final_quality', 'neutral')
        summary_line = get_summary_line(final_quality)
        return {
            "promo_line": summary_line,
            "is_summary": True,
            "commentary_line": "",
            "score": beat.get('score', 0),
            "momentum": momentum,
            "confidence": confidence
        }
    
    # Generate promo line
    promo_line = get_promo_line(tone, theme, phase)
    
    # Handle momentum cash-in first (highest priority)
    if beat.get("cash_in_used", False):
        spent = -beat.get("momentum_gain", 0)
        boost = beat.get("confidence_boost", 0)
        cash_in_line = get_cash_in_commentary(spent, boost)
        return {
            "promo_line": promo_line,
            "commentary_line": cash_in_line,
            "is_cash_in": True,  # New flag for UI formatting
            "score": beat.get('score', 0),  # Include score for UI coloring
            "momentum": momentum,  # Include current momentum
            "momentum_gain": spent,  # Include momentum spent
            "confidence": confidence,  # Include current confidence
            "confidence_boost": boost  # Include confidence boost
        }
    
    # Get phase-appropriate commentary
    phase_quality = 'perfect' if quality == 'perfect' else 'good' if quality in ['excellent', 'good'] else 'bad'
    phase_comment = random.choice(PHASE_COMMENTS[commentary_phase][phase_quality])
    
    # Build final commentary
    commentary_parts = []
    
    # Add phase-specific comment first
    commentary_parts.append(phase_comment)
    
    # Check special triggers
    if quality in ["good", "excellent"] and momentum < 30:
        commentary_parts.append(get_special_trigger_comment('underdog_strike'))
    elif quality in ["bad", "terrible"] and momentum > 80 and commentary_phase == 'end':
        commentary_parts.append(get_special_trigger_comment('fumble_clutch'))
    elif quality == "perfect" and confidence < 30:
        commentary_parts.append(get_special_trigger_comment('out_of_nowhere'))
    elif beat.get('bad_streak', 0) >= 2 and confidence < 40:
        commentary_parts.append(get_special_trigger_comment('collapse_spiral'))
    elif confidence > 90 and quality in ["excellent", "perfect"]:
        commentary_parts.append(get_special_trigger_comment('confidence_peak'))
    elif momentum > 85 and quality in ["good", "excellent", "perfect"]:
        commentary_parts.append(get_special_trigger_comment('momentum_takeover'))
    elif commentary_phase == "beginning" and quality == "perfect":
        commentary_parts.append(get_special_trigger_comment('early_surprise'))
    elif quality in ["good", "excellent"] and commentary_phase == "end" and confidence > 70:
        commentary_parts.append(get_special_trigger_comment('late_recovery'))
    elif quality == "flop" and momentum > 70:
        commentary_parts.append(get_special_trigger_comment('wasted_opportunity'))
    elif beat.get('improving_streak', 0) >= 2:
        commentary_parts.append(get_special_trigger_comment('ignition_point'))
    elif commentary_phase == "beginning" and quality in ["bad", "terrible", "flop"]:
        commentary_parts.append(get_special_trigger_comment('icy_opening'))
    elif commentary_phase == "end" and quality == "perfect":
        commentary_parts.append(get_special_trigger_comment('mic_drop'))
    
    # Add contextual commentary if no special triggers hit
    if len(commentary_parts) == 1:  # Only has phase comment
        commentary_parts.append(get_quality_comment(quality))
        
        # Add momentum context
        if momentum > 85:
            commentary_parts.append(get_context_comment('momentum', 'dominant'))
        elif momentum > 75:
            commentary_parts.append(get_context_comment('momentum', 'strong'))
        elif momentum < 25:
            commentary_parts.append(get_context_comment('momentum', 'weak'))
            
        # Add confidence context
        if confidence > 90:
            commentary_parts.append(get_context_comment('confidence', 'high'))
        elif confidence < 25:
            commentary_parts.append(get_context_comment('confidence', 'low'))
    
    return {
        "promo_line": promo_line,
        "commentary_line": " ".join(commentary_parts),
        "is_cash_in": False,
        "score": beat.get('score', 0),
        "momentum": momentum,  # Include current momentum
        "momentum_gain": beat.get("momentum_gain", 0),  # Include momentum gain/loss
        "confidence": confidence,  # Include current confidence
        "confidence_boost": beat.get("confidence_boost", 0)  # Include confidence boost
    } 