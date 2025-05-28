# Promo lines organized by phase, tone, and theme
import random

PROMO_LINES = {
    "opening": {
        "boast": {
            "legacy": [
                "I've been dominating this ring longer than most of you have been watching!",
                "My legacy in this business speaks for itself.",
                "When they write the history books of this sport, my name will be in every chapter."
            ],
            "dominance": [
                "Nobody in that locker room can touch what I bring to this ring.",
                "I stand alone at the top of this mountain.",
                "I don't just compete, I dominate everything I touch in this business."
            ],
            "betrayal": [
                "After what happened, I've got a lot to say and you all need to hear it.",
                "Betrayal makes you rethink who your real friends are in this business.",
                "Trust is earned, and in this business, it's hard to come by."
            ],
            "power": [
                "Power isn't just about strength, it's about control.",
                "In this ring, power is the only language that matters.",
                "They say power corrupts, but I say power reveals who you truly are."
            ],
            "comeback": [
                "They counted me out, but here I stand, stronger than ever.",
                "Setbacks only fuel my comeback story.",
                "Every time I get knocked down, I get back up stronger."
            ],
            "respect": [
                "Respect in this business isn't given, it's earned through blood and sweat.",
                "I've paid my dues, and now I demand the respect I deserve.",
                "This isn't about titles, it's about respect."
            ],
            "generic": [
                "Let me tell you something...",
                "Listen up, because I'm only saying this once.",
                "I've got something to get off my chest tonight."
            ]
        },
        "callout": {
            "legacy": [
                "opponent, your so-called legacy doesn't hold a candle to mine!",
                "I've been watching you, opponent, and you're not half the competitor I am.",
                "opponent, you talk about making history, but I AM history in this business!"
            ],
            "dominance": [
                "opponent, you think you're at the top? You haven't seen dominance until you've faced me!",
                "I'm calling you out right here, right now, opponent!",
                "opponent, step into this ring if you dare."
            ],
            "betrayal": [
                "opponent, after what you did, you've got a lot to answer for!",
                "opponent, your betrayal showed everyone your true colors.",
                "I trusted you, opponent, and that was my mistake."
            ],
            "power": [
                "opponent, you'll feel real power when you step in this ring with me!",
                "You call yourself powerful, opponent? Let me show you what real power looks like!",
                "opponent, your power is nothing compared to what I bring to this ring."
            ],
            "comeback": [
                "opponent, you thought you ended my career, but I'm back and coming for you!",
                "opponent, my comeback story starts with taking you down!",
                "You've been on top while I was gone, opponent, but that ends now!"
            ],
            "respect": [
                "opponent, you've disrespected me for the last time!",
                "You want my respect, opponent? You have to earn it in this ring!",
                "opponent, respect is earned, not given, and you haven't earned anything!"
            ],
            "generic": [
                "opponent, I'm talking to you!",
                "opponent, you and me, one-on-one!",
                "I'm calling you out, opponent!"
            ]
        },
        "insult": {
            "legacy": [
                "opponent, your so-called legacy is a joke compared to mine!",
                "opponent, you're just a footnote in the history of this business.",
                "What legacy, opponent? You'll be forgotten next week!"
            ],
            "dominance": [
                "opponent, you're pathetic! You couldn't dominate a high school gym!",
                "I've seen more intimidating teddy bears than you, opponent!",
                "opponent, you're soft, and everyone knows it!"
            ],
            "betrayal": [
                "opponent, you're nothing but a snake in the grass!",
                "I trusted you, opponent, and you stabbed me in the back!",
                "opponent, your betrayal shows what a coward you really are!"
            ],
            "power": [
                "opponent, you couldn't knock down a house of cards!",
                "You call that power, opponent? My grandmother hits harder than you!",
                "opponent, you're the weakest link in that locker room!"
            ],
            "comeback": [
                "opponent, you thought you could keep me down? Think again!",
                "While you were celebrating, opponent, I was getting stronger!",
                "opponent, you're about to wish I never came back!"
            ],
            "respect": [
                "opponent, you haven't earned any respect in this business!",
                "Nobody respects you, opponent, and for good reason!",
                "opponent, respect is earned, and you've earned nothing but contempt!"
            ],
            "generic": [
                "opponent, you're pathetic!",
                "I've seen better wrestlers in a kiddie pool, opponent!",
                "opponent, you're a joke in this business!"
            ]
        },
        "humble": {
            "legacy": [
                "I'm grateful for every moment I've had in this business.",
                "This legacy we build is bigger than any one person.",
                "I stand on the shoulders of the legends who came before me."
            ],
            "dominance": [
                "Winning isn't everything, it's about how you compete.",
                "True dominance comes from respect, not intimidation.",
                "I don't need to brag about being the best, I just need to be it."
            ],
            "betrayal": [
                "Even after what happened, I've learned to forgive, but not forget.",
                "Betrayal teaches you who to trust in this business.",
                "When you're betrayed, you have two choices: break down or break through."
            ],
            "power": [
                "Real power comes from within, not from intimidation.",
                "The strongest power is the ability to lift others up.",
                "I don't flaunt my power, I use it when necessary."
            ],
            "comeback": [
                "Every setback is a setup for a comeback.",
                "I'm grateful for the journey, both the highs and lows.",
                "This comeback isn't just for me, it's for everyone who believed in me."
            ],
            "respect": [
                "I respect everyone in that locker room, even my opponents.",
                "Respect is a two-way street in this business.",
                "Win or lose, respect is what matters most to me."
            ],
            "generic": [
                "I'm honored to be here tonight.",
                "I'm grateful for all the support I've received.",
                "This journey wouldn't be possible without all of you."
            ]
        }
    },
    "middle": {
        "boast": {
            "legacy": [
                "My accomplishments speak for themselves.",
                "I've forgotten more about this business than most will ever learn.",
                "My legacy is written in gold and can never be erased."
            ],
            "dominance": [
                "I don't just win matches, I dominate opponents.",
                "There's levels to this game, and I'm at the top.",
                "Nobody can match my intensity in this ring."
            ],
            "betrayal": [
                "After what happened, I learned to trust only myself.",
                "Betrayal made me stronger, more focused, more dangerous.",
                "The betrayal I suffered only fueled my determination."
            ],
            "power": [
                "My power is unmatched in this company.",
                "When I hit you, you stay hit.",
                "Power isn't just physical—it's mental, and I've mastered both."
            ],
            "comeback": [
                "This comeback is the greatest chapter of my career.",
                "They said I was finished, but I'm just getting started.",
                "My comeback will be remembered long after your career is forgotten."
            ],
            "respect": [
                "I've earned every ounce of respect I have in this business.",
                "Respect is earned through blood, sweat, and sacrifice.",
                "My respect in this industry was paid for with years of dedication."
            ],
            "generic": [
                "Nobody does it better than me.",
                "I'm in a league of my own.",
                "There's not a single person who can match what I bring."
            ]
        },
        "callout": {
            "legacy": [
                "opponent, your legacy doesn't even begin to compare to mine!",
                "While you were playing pretend, opponent, I was making history!",
                "opponent, history will remember me, not you!"
            ],
            "dominance": [
                "opponent, you've never faced someone like me before!",
                "I'm going to dominate you, opponent, like you've never experienced!",
                "opponent, prepare to be thoroughly outclassed!"
            ],
            "betrayal": [
                "opponent, your betrayal only showed your true colors!",
                "You thought betraying me would break me, opponent, but it only made me stronger!",
                "opponent, you'll regret the day you crossed me!"
            ],
            "power": [
                "opponent, you'll feel my power when we meet in that ring!",
                "My power will shatter you, opponent!",
                "opponent, you have no idea what kind of force you're up against!"
            ],
            "comeback": [
                "opponent, you thought I was finished, but my comeback starts with taking you down!",
                "You enjoyed your time on top while I was gone, opponent, but the king has returned!",
                "My comeback story will be written over your broken body, opponent!"
            ],
            "respect": [
                "opponent, you've never shown proper respect for this business!",
                "I demand respect, opponent, and I'll take it from you if necessary!",
                "opponent, respect is earned through battle, and you're about to earn mine the hard way!"
            ],
            "generic": [
                "opponent, I'm coming for you next!",
                "You're in my sights now, opponent!",
                "opponent, your time is running out!"
            ]
        },
        "insult": {
            "legacy": [
                "opponent, what legacy? You'll be forgotten as soon as you retire!",
                "Your so-called accomplishments are a joke, opponent!",
                "opponent, you're a footnote in history, nothing more!"
            ],
            "dominance": [
                "opponent, you couldn't dominate a high school gym class!",
                "You call that dominance, opponent? I've seen scarier puppies!",
                "opponent, you're soft and everyone knows it!"
            ],
            "betrayal": [
                "opponent, you're the biggest snake I've ever met in this business!",
                "You're nothing but a backstabbing coward, opponent!",
                "opponent, your betrayal shows what kind of person you really are!"
            ],
            "power": [
                "opponent, you couldn't knock over a paper cup!",
                "Your power is an illusion, opponent, just like your talent!",
                "opponent, my grandmother hits harder than you!"
            ],
            "comeback": [
                "opponent, you thought you could keep me down? Think again!",
                "While you were celebrating, opponent, I was getting stronger!",
                "opponent, your career is about to take a nosedive while mine rises again!"
            ],
            "respect": [
                "Nobody respects you, opponent, and for good reason!",
                "opponent, you haven't earned any respect in this business!",
                "Respect? You? That's the funniest joke I've heard all year, opponent!"
            ],
            "generic": [
                "opponent, you're pathetic!",
                "I've seen better wrestlers at the county fair, opponent!",
                "opponent, you're a joke in this business!"
            ]
        },
        "humble": {
            "legacy": [
                "A true legacy is built on respect, not just victories.",
                "I'm just one chapter in the ongoing story of this great sport.",
                "I hope my legacy inspires the next generation."
            ],
            "dominance": [
                "I don't need to dominate others to prove my worth.",
                "True strength comes from lifting others up, not putting them down.",
                "I compete against myself first and foremost."
            ],
            "betrayal": [
                "Even after betrayal, I choose to focus on moving forward.",
                "Forgiveness is harder than revenge, but more rewarding.",
                "I won't let past betrayals define my future."
            ],
            "power": [
                "True power is knowing when not to use it.",
                "My strength comes from those who support me.",
                "Power without compassion is just bullying."
            ],
            "comeback": [
                "This comeback isn't just for me, it's for everyone who believed in me.",
                "Every setback is a setup for something greater.",
                "I'm grateful for the journey, both the highs and lows."
            ],
            "respect": [
                "I respect everyone in that locker room, especially my opponents.",
                "Respect isn't demanded, it's earned through consistent actions.",
                "Win or lose, mutual respect is what matters most."
            ],
            "generic": [
                "I'm grateful for the opportunity to compete.",
                "It's an honor to be part of this tradition.",
                "I never take any of this for granted."
            ]
        }
    },
    "closing": {
        "boast": {
            "legacy": [
                "When all is said and done, my legacy will stand the test of time!",
                "The history books will remember my name long after I'm gone!",
                "My legacy in this business is written in gold!"
            ],
            "dominance": [
                "I don't just compete, I dominate everything I touch!",
                "There's no one in this company who can match my dominance!",
                "I stand alone at the pinnacle of this industry!"
            ],
            "betrayal": [
                "After the betrayal I suffered, I trust no one but myself!",
                "Betrayal made me stronger than I've ever been!",
                "What doesn't kill me only makes me more dangerous!"
            ],
            "power": [
                "My power is unmatched in this ring!",
                "You haven't seen real power until you've stepped in the ring with me!",
                "Power recognizes power, and there's none greater than mine!"
            ],
            "comeback": [
                "This comeback is just the beginning of the greatest chapter of my career!",
                "They said I was finished, but I'm just getting started!",
                "My comeback will be the stuff of legend!"
            ],
            "respect": [
                "I've earned every ounce of respect I have in this business!",
                "Respect is earned through blood, sweat, and sacrifice!",
                "My respect in this industry was paid for with years of dedication!"
            ],
            "generic": [
                "Nobody does it better than me!",
                "I'm in a league of my own!",
                "That's not a threat, that's a guarantee!"
            ]
        },
        "callout": {
            "legacy": [
                "opponent, at the next event, I'll show you what a real legacy looks like!",
                "opponent, your legacy ends when you step in the ring with me!",
                "I'm coming for you, opponent, and I'm bringing history with me!"
            ],
            "dominance": [
                "opponent, at the next show, I will dominate you like you've never been dominated before!",
                "There won't be anything left of you when I'm done, opponent!",
                "opponent, you're about to be my next victim!"
            ],
            "betrayal": [
                "opponent, your betrayal comes with a price, and I'm collecting at the next event!",
                "You'll regret the day you crossed me, opponent!",
                "opponent, payback is coming, and it's going to be painful!"
            ],
            "power": [
                "opponent, you'll feel my full power at the next show!",
                "My power will break you, opponent!",
                "opponent, you have no idea what kind of force you're about to face!"
            ],
            "comeback": [
                "opponent, my comeback tour runs right through you!",
                "You enjoyed your time on top while I was gone, opponent, but the king has returned!",
                "My comeback story continues with your defeat, opponent!"
            ],
            "respect": [
                "opponent, at the next event, I'll teach you the meaning of respect!",
                "I demand respect, opponent, and I'll take it from you if necessary!",
                "opponent, respect is earned through battle, and you're about to earn mine the hard way!"
            ],
            "generic": [
                "opponent, you and me, one on one, at the next event!",
                "I'm calling you out, opponent! Let's settle this once and for all!",
                "opponent, your time is up!"
            ]
        },
        "insult": {
            "legacy": [
                "opponent, after I'm done with you, your so-called legacy will be nothing but a bad memory!",
                "Your legacy is a joke, opponent, just like your career!",
                "opponent, history will remember you as nothing but my stepping stone!"
            ],
            "dominance": [
                "opponent, you're pathetic! You couldn't dominate a kindergarten playground!",
                "I've seen more intimidating teddy bears than you, opponent!",
                "opponent, I'm going to embarrass you in front of the whole world!"
            ],
            "betrayal": [
                "opponent, your betrayal shows what a spineless coward you really are!",
                "You're nothing but a snake, opponent, and I'm the snake charmer!",
                "opponent, traitors like you always get what's coming to them!"
            ],
            "power": [
                "opponent, you're so weak, a strong breeze could knock you over!",
                "Your power is an illusion, opponent, just like your talent!",
                "opponent, my grandmother hits harder than you!"
            ],
            "comeback": [
                "opponent, you thought you ended my career? I'm back to end yours!",
                "My comeback will be legendary, opponent, and your downfall will be part of that story!",
                "opponent, you're just a footnote in my comeback story!"
            ],
            "respect": [
                "Nobody respects you, opponent, and after I'm done with you, they never will!",
                "opponent, you haven't earned any respect in this business!",
                "Respect? You? That's the funniest joke I've heard all year, opponent!"
            ],
            "generic": [
                "opponent, you're absolutely pathetic!",
                "I've seen better wrestlers at the county fair, opponent!",
                "opponent, you're the biggest joke in this business!"
            ]
        },
        "humble": {
            "legacy": [
                "Win or lose, I hope to leave this business better than I found it.",
                "A true legacy is measured by the lives you touch, not just the titles you win.",
                "I'm just one chapter in the ongoing story of this great sport."
            ],
            "dominance": [
                "True victory comes from overcoming your own limitations.",
                "I don't need to dominate others to prove my worth.",
                "The real competition is always with yourself."
            ],
            "betrayal": [
                "Even after betrayal, I choose forgiveness over bitterness.",
                "Betrayal teaches us who to trust, but shouldn't make us stop trusting.",
                "I won't let past betrayals define my future."
            ],
            "power": [
                "Real power comes from using your platform to help others.",
                "The strongest power is knowing when not to use it.",
                "True strength is measured by how you lift others up."
            ],
            "comeback": [
                "This comeback isn't just for me, it's for everyone who never gave up.",
                "Every setback is a setup for something greater.",
                "I'm grateful for the journey, both the highs and lows."
            ],
            "respect": [
                "Win or lose, mutual respect is what matters most.",
                "I respect everyone in that locker room, especially my opponents.",
                "Respect isn't demanded, it's earned through consistent actions."
            ],
            "generic": [
                "I'm blessed to do what I love in front of all of you.",
                "Thank you all for your support through thick and thin.",
                "It's an honor to be part of this tradition."
            ]
        }
    }
}

def get_versus_promo_line(tone, phase, position):
    """Get a promo line for versus promos based on tone, phase and position."""
    # Versus promo lines by tone, phase and position
    versus_lines = {
        "boast": {
            "opening": {
                "first": [
                    "[WRESTLER] steps into the center of the ring. 'Let me tell you all why I'm the best in this business.'",
                    "'Ladies and gentlemen, you're looking at the greatest superstar of all time!' [WRESTLER] proclaims proudly.",
                    "[WRESTLER] grabs the mic with confidence. 'There's not a person in this arena who can touch my legacy!'",
                    "'When they write the history books of this industry, my name will be on every page!' [WRESTLER] boasts."
                ],
                "response": [
                    "[WRESTLER] laughs. 'You think you're something special? Let me remind you who I am.'",
                    "'That's cute, [OPPONENT]. But while you're talking, I'm making history every single night.'",
                    "[WRESTLER] shakes their head. 'I've accomplished more in a month than you have in your entire career.'",
                    "'I don't need to respond to [OPPONENT]. My championships speak for themselves.'"
                ]
            },
            "middle": {
                "first": [
                    "'Let's be honest, [OPPONENT]. You're standing in the ring with greatness right now.'",
                    "[WRESTLER] points to the crowd. 'They didn't come to see you. They came to see me!'",
                    "'I've beaten legends that make you look like an amateur, [OPPONENT].'",
                    "[WRESTLER] paces confidently. 'You're just another name on my list of conquests.'"
                ],
                "response": [
                    "[WRESTLER] smirks. 'You think that impresses me? I eat challenges like you for breakfast.'",
                    "'[OPPONENT], I've forgotten more about this business than you'll ever know.'",
                    "[WRESTLER] laughs off [OPPONENT]'s words. 'You're not even in my league.'",
                    "'The difference between us is simple: I'm [WRESTLER], and you're... well, you're just you.'"
                ]
            },
            "ending": {
                "first": [
                    "'When this is all said and done, [OPPONENT], they'll remember my name, not yours.'",
                    "[WRESTLER] raises their arms triumphantly. 'This is what a real champion looks like!'",
                    "'After I'm done with you, [OPPONENT], you'll be begging for my autograph.'",
                    "[WRESTLER] points to the exit. 'There's the door. Use it before I embarrass you even more.'"
                ],
                "response": [
                    "[WRESTLER] laughs confidently. 'Is that all you've got? I've had tougher challenges from rookies.'",
                    "'When I'm done with you, [OPPONENT], they'll be chanting MY name, not yours.'",
                    "[WRESTLER] waves dismissively. 'You've had your moment. Now it's time for a real star to shine.'",
                    "'Remember this moment, [OPPONENT]. It's the closest you'll ever get to greatness.'"
                ]
            }
        },
        "challenge": {
            "opening": {
                "first": [
                    "[WRESTLER] points directly at [OPPONENT]. 'You think you're so tough? Prove it right here, right now!'",
                    "'[OPPONENT], I'm calling you out! Let's settle this once and for all!'",
                    "[WRESTLER] paces like a predator. 'I've been waiting for this moment to finally shut you up.'",
                    "'You've been running your mouth for too long, [OPPONENT]. Time to back it up!'"
                ],
                "response": [
                    "[WRESTLER] steps forward aggressively. 'You want to challenge ME? You have no idea what you're in for.'",
                    "'[OPPONENT], you just made the biggest mistake of your career challenging me.'",
                    "[WRESTLER] rolls up their sleeves. 'I accept your challenge, and I'll raise you one beating you won't forget.'",
                    "'Be careful what you wish for, [OPPONENT]. You might just get it.'"
                ]
            },
            "middle": {
                "first": [
                    "'I'm not just going to beat you, [OPPONENT]. I'm going to make an example out of you.'",
                    "[WRESTLER] slams their fist into their palm. 'Anytime, anywhere. Name the place.'",
                    "'You want to test yourself against the best? Then bring everything you've got!'",
                    "[WRESTLER] gets in [OPPONENT]'s face. 'No excuses when I beat you clean in the middle of this ring.'"
                ],
                "response": [
                    "[WRESTLER] steps even closer. 'You think that scares me? I eat challenges like this for breakfast.'",
                    "'[OPPONENT], you just signed your own defeat. I accept, and you'll regret it.'",
                    "[WRESTLER] nods slowly. 'Challenge accepted. But remember, you asked for this.'",
                    "'You want to test me? Fine. But don't cry when I break you in half.'"
                ]
            },
            "ending": {
                "first": [
                    "'This Sunday, [OPPONENT], no excuses, no running away. Just you and me.'",
                    "[WRESTLER] gets nose to nose with [OPPONENT]. 'One match. Winner takes all.'",
                    "'I'm challenging you right here, right now. Do you accept, or are you a coward?'",
                    "[WRESTLER] holds up a title belt. 'This is what you want? Come and take it if you can!'"
                ],
                "response": [
                    "[WRESTLER] nods confidently. 'Consider your challenge accepted. And your career shortened.'",
                    "'[OPPONENT], I hope you're ready to back up those words with action.'",
                    "[WRESTLER] extends a hand. 'Deal. But don't say I didn't warn you.'",
                    "'Challenge accepted. And after I win, you'll never get another shot.'"
                ]
            }
        },
        "insult": {
            "opening": {
                "first": [
                    "[WRESTLER] looks disgusted. 'Look at [OPPONENT], the biggest joke in this company.'",
                    "'Ladies and gentlemen, behold [OPPONENT], professional wrestling's greatest disappointment!'",
                    "[WRESTLER] laughs mockingly. 'I can't believe they actually pay you to embarrass yourself each week.'",
                    "'[OPPONENT], you are without a doubt the most pathetic excuse for a wrestler I've ever seen.'"
                ],
                "response": [
                    "[WRESTLER] slow claps sarcastically. 'Wow, [OPPONENT], did you stay up all night thinking of that one?'",
                    "'That's rich coming from a two-bit hack like you, [OPPONENT].'",
                    "[WRESTLER] looks around confused. 'I'm sorry, was that supposed to hurt my feelings?'",
                    "'At least I have talent, [OPPONENT]. What's your excuse?'"
                ]
            },
            "middle": {
                "first": [
                    "'You're nothing but a footnote in my career, [OPPONENT]. A forgettable chapter at best.'",
                    "[WRESTLER] sneers. 'Look at you, trying so hard yet achieving so little.'",
                    "'The difference between us is simple: talent. I have it, you don't.'",
                    "[WRESTLER] points at [OPPONENT]'s face. 'Even your family changes the channel when you come on.'"
                ],
                "response": [
                    "[WRESTLER] laughs derisively. 'That's the best you've got? Pathetic, just like your career.'",
                    "'[OPPONENT], your words are as weak as your in-ring skills.'",
                    "[WRESTLER] mimes yawning. 'I've heard better insults from rookies on their first day.'",
                    "'Keep talking, [OPPONENT]. It's the only thing you're even remotely good at.'"
                ]
            },
            "ending": {
                "first": [
                    "'After I'm done with you, [OPPONENT], you'll be begging for a job at the local fast food joint.'",
                    "[WRESTLER] looks [OPPONENT] up and down with disgust. 'You're not even worth my time.'",
                    "'You're nothing but a stepping stone in my journey to greatness, [OPPONENT].'",
                    "[WRESTLER] mimics wiping dust off their shoulder. 'That's all you are to me. Dust to be brushed aside.'"
                ],
                "response": [
                    "[WRESTLER] smirks. 'Big words from someone with such a small talent.'",
                    "'I'd insult you back, [OPPONENT], but it looks like genetics already did that job for me.'",
                    "[WRESTLER] laughs harshly. 'When this is over, you'll be remembered as just another victim.'",
                    "'Keep dreaming, [OPPONENT]. That's as close as you'll ever get to beating me.'"
                ]
            }
        },
        "callout": {
            "opening": {
                "first": [
                    "[WRESTLER] points accusingly. '[OPPONENT], you've been ducking me for months, and everyone knows it!'",
                    "'I'm calling you out, [OPPONENT]! Stop hiding and face me like a real competitor!'",
                    "[WRESTLER] paces angrily. 'The truth about [OPPONENT] needs to be heard, and I'm the one to tell it!'",
                    "'[OPPONENT], I'm tired of your lies and excuses. It ends tonight!'"
                ],
                "response": [
                    "[WRESTLER] steps forward aggressively. 'You want to call ME out? That's rich!'",
                    "'[OPPONENT], you've got some nerve questioning my integrity!'",
                    "[WRESTLER] laughs bitterly. 'That's funny coming from you of all people.'",
                    "'Let's get one thing straight, [OPPONENT]. You don't get to question me. Ever.'"
                ]
            },
            "middle": {
                "first": [
                    "'Everyone in that locker room knows you're a fraud, [OPPONENT]. And now so does the world.'",
                    "[WRESTLER] points to the crowd. 'They see right through you, just like I do!'",
                    "'You talk about respect? You don't even know the meaning of the word, [OPPONENT]!'",
                    "[WRESTLER] circles [OPPONENT]. 'Your time of lying and cheating your way to the top is over!'"
                ],
                "response": [
                    "[WRESTLER] steps closer. 'You dare question my achievements? Let's compare resumes right now!'",
                    "'[OPPONENT], your accusations just show how desperate you are.'",
                    "[WRESTLER] shakes their head. 'The only fraud in this ring is the one I'm looking at.'",
                    "'Rich words from someone who couldn't lace my boots on their best day.'"
                ]
            },
            "ending": {
                "first": [
                    "'The fans deserve better than what you give them, [OPPONENT], and I'm here to deliver!'",
                    "[WRESTLER] points to the stage. 'Come out and face the truth, [OPPONENT]! I'm waiting!'",
                    "'I'm exposing you for what you really are, [OPPONENT]: a coward and a fraud!'",
                    "[WRESTLER] challenges with open arms. 'Prove me wrong if you can, [OPPONENT]! I dare you!'"
                ],
                "response": [
                    "[WRESTLER] stands tall. 'You've called me out, now you'll have to deal with the consequences.'",
                    "'[OPPONENT], you just wrote a check your body can't cash.'",
                    "[WRESTLER] approaches menacingly. 'You wanted my attention? Well, now you have it.'",
                    "'Be careful what you wish for, [OPPONENT]. You might just get it.'"
                ]
            }
        },
        "humble": {
            "opening": {
                "first": [
                    "[WRESTLER] speaks calmly. 'I don't need to boast or brag. My actions speak for themselves.'",
                    "'I respect you, [OPPONENT], but that won't stop me from giving everything I have.'",
                    "[WRESTLER] nods respectfully. 'You're good, [OPPONENT]. One of the best. But so am I.'",
                    "'This isn't about who talks the best game. It's about who performs when it matters.'"
                ],
                "response": [
                    "[WRESTLER] nods thoughtfully. 'I hear your words, [OPPONENT], and I respect your confidence.'",
                    "'I don't need to match your attitude, [OPPONENT]. I'll let my skills do the talking.'",
                    "[WRESTLER] remains composed. 'You can try to get under my skin, but I'm focused on one thing: winning.'",
                    "'Your opinion of me doesn't define who I am or what I can do.'"
                ]
            },
            "middle": {
                "first": [
                    "'I've worked too hard to get here to let anyone, even you [OPPONENT], stand in my way.'",
                    "[WRESTLER] speaks earnestly. 'This isn't personal. It's about being the best I can be.'",
                    "'You deserve respect for what you've accomplished, [OPPONENT]. But so do I.'",
                    "[WRESTLER] extends a hand. 'May the best competitor win when we face off.'"
                ],
                "response": [
                    "[WRESTLER] remains calm. 'Your words don't change my resolve or my preparation.'",
                    "'I don't need to match your intensity, [OPPONENT]. I just need to beat you.'",
                    "[WRESTLER] nods. 'Fair points. But when we meet in that ring, talk won't matter.'",
                    "'I appreciate your passion, [OPPONENT]. I really do. But it won't be enough.'"
                ]
            },
            "ending": {
                "first": [
                    "'When all is said and done, [OPPONENT], we'll shake hands, but I plan on being the victor.'",
                    "[WRESTLER] speaks with quiet confidence. 'I respect everything you stand for. That's why beating you means so much.'",
                    "'Win or lose, [OPPONENT], the fans will get our very best. That's a promise.'",
                    "[WRESTLER] nods respectfully. 'Let's give them a match they'll never forget.'"
                ],
                "response": [
                    "[WRESTLER] offers a respectful nod. 'May the best competitor win. But know I'm bringing everything I have.'",
                    "'I accept your challenge with humility and determination, [OPPONENT].'",
                    "[WRESTLER] extends a hand. 'When this is over, we'll both be better for it.'",
                    "'I look forward to proving myself against a competitor of your caliber.'"
                ]
            }
        }
    }
    
    # If the requested tone, phase or position isn't available, return a generic line
    if tone not in versus_lines or phase not in versus_lines[tone] or position not in versus_lines[tone][phase]:
        return "[WRESTLER] faces off against [OPPONENT] in an intense exchange!"
    
    # Return a random line from the appropriate category
    lines = versus_lines[tone][phase][position]
    return random.choice(lines) 