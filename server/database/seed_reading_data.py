"""
Seed script for reading practice data
Run with: python -m database.seed_reading_data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.models.reading import ReadingItem, ReadingQuestion


def seed_reading_data():
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(ReadingItem).first()
        if existing:
            print("Reading data already exists. Skipping seed.")
            return

        # EASY LEVEL PASSAGES
        easy_passage_1 = ReadingItem(
            title="The History of Coffee",
            difficulty="easy",
            skill_tags=["vocabulary", "main-idea", "detail"],
            passage="""Coffee is one of the most popular beverages in the world. The coffee plant originated in Ethiopia, where legend says a goat herder named Kaldi first discovered the energizing effects of coffee beans. He noticed that his goats became unusually energetic after eating berries from a certain tree.

From Ethiopia, coffee spread to the Arabian Peninsula. By the 15th century, coffee was being grown in Yemen, and from there it reached Turkey, where the world's first coffee houses opened. These establishments quickly became centers of social activity and communication.

Coffee reached Europe in the 17th century, though it initially faced resistance from some religious leaders who called it "the bitter invention of Satan." However, Pope Clement VIII tasted it and gave it his blessing, helping coffee become acceptable to Christians. Coffee houses began opening across Europe, becoming important meeting places for intellectuals and businesspeople.

Today, coffee is grown in over 70 countries, primarily in regions near the equator. Brazil is the world's largest coffee producer, followed by Vietnam and Colombia. Coffee cultivation provides livelihoods for millions of small farmers worldwide."""
        )

        db.add(easy_passage_1)
        db.flush()

        questions_easy_1 = [
            ReadingQuestion(
                reading_item_id=easy_passage_1.id,
                question="According to the passage, who first discovered the energizing effects of coffee?",
                options={"A": "A religious leader", "B": "A goat herder named Kaldi", "C": "Pope Clement VIII", "D": "A farmer in Yemen"},
                correct_answer="B",
                explanation="The passage states that 'legend says a goat herder named Kaldi first discovered the energizing effects of coffee beans.'",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=easy_passage_1.id,
                question="What is the main idea of this passage?",
                options={"A": "Coffee is unhealthy", "B": "The history and spread of coffee", "C": "How to grow coffee beans", "D": "Religious controversies about coffee"},
                correct_answer="B",
                explanation="The passage traces coffee's journey from Ethiopia to becoming a global beverage, making 'The history and spread of coffee' the main idea.",
                skill_category="main-idea"
            ),
            ReadingQuestion(
                reading_item_id=easy_passage_1.id,
                question="The word 'originated' in the first paragraph is closest in meaning to:",
                options={"A": "was consumed", "B": "was banned", "C": "came from", "D": "was exported"},
                correct_answer="C",
                explanation="'Originated' means to have its origin or source, which is closest to 'came from.'",
                skill_category="vocabulary"
            ),
            ReadingQuestion(
                reading_item_id=easy_passage_1.id,
                question="According to the passage, where is most coffee grown today?",
                options={"A": "In Europe", "B": "In Ethiopia only", "C": "Near the equator", "D": "In Turkey"},
                correct_answer="C",
                explanation="The passage states that 'coffee is grown in over 70 countries, primarily in regions near the equator.'",
                skill_category="detail"
            )
        ]

        for q in questions_easy_1:
            db.add(q)

        # MEDIUM LEVEL PASSAGE
        medium_passage_1 = ReadingItem(
            title="The Impact of Urbanization on Wildlife",
            difficulty="medium",
            skill_tags=["inference", "vocabulary", "cause-effect"],
            passage="""Urbanization, the process by which rural areas develop into cities, has dramatically accelerated in recent decades. As of 2020, more than half of the world's population lives in urban areas, and this proportion is expected to increase to 68% by 2050. While urbanization brings economic opportunities and improved access to services, it also poses significant challenges to wildlife and ecosystems.

The expansion of cities typically results in habitat fragmentation, where large, continuous habitats are divided into smaller, isolated patches. This fragmentation can be particularly detrimental to species that require large territories or those that migrate seasonally. For example, many large predators need vast hunting grounds to maintain viable populations, and habitat fragmentation can lead to their local extinction.

However, some species have demonstrated remarkable adaptability to urban environments. Peregrine falcons, once endangered, now nest on tall buildings in cities, using them as substitutes for their natural cliff habitats. Similarly, urban parks and gardens can serve as refuges for various bird species, insects, and small mammals. Research has shown that well-designed green spaces within cities can support surprisingly high levels of biodiversity.

The relationship between urbanization and wildlife is complex and varies depending on the species and the nature of urban development. Cities that incorporate green infrastructure—such as parks, green roofs, and wildlife corridors—tend to support more diverse wildlife populations than those dominated by concrete and asphalt. Urban planning that considers ecological needs alongside human requirements represents a promising approach to creating more sustainable cities."""
        )

        db.add(medium_passage_1)
        db.flush()

        questions_medium_1 = [
            ReadingQuestion(
                reading_item_id=medium_passage_1.id,
                question="What can be inferred about habitat fragmentation from the passage?",
                options={
                    "A": "It only affects small animals",
                    "B": "It has no impact on bird populations",
                    "C": "It is more harmful to species requiring large territories",
                    "D": "It increases biodiversity in all cases"
                },
                correct_answer="C",
                explanation="The passage states that fragmentation 'can be particularly detrimental to species that require large territories,' allowing us to infer it's more harmful to such species.",
                skill_category="inference"
            ),
            ReadingQuestion(
                reading_item_id=medium_passage_1.id,
                question="According to the passage, what percentage of the world's population is expected to live in urban areas by 2050?",
                options={"A": "50%", "B": "58%", "C": "68%", "D": "78%"},
                correct_answer="C",
                explanation="The passage explicitly states that the proportion 'is expected to increase to 68% by 2050.'",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=medium_passage_1.id,
                question="The word 'viable' in paragraph 2 is closest in meaning to:",
                options={"A": "sustainable", "B": "large", "C": "aggressive", "D": "isolated"},
                correct_answer="A",
                explanation="'Viable' means capable of working successfully or continuing to exist, which is closest to 'sustainable.'",
                skill_category="vocabulary"
            ),
            ReadingQuestion(
                reading_item_id=medium_passage_1.id,
                question="The example of peregrine falcons is used to illustrate:",
                options={
                    "A": "The extinction of urban wildlife",
                    "B": "Species' ability to adapt to cities",
                    "C": "The dangers of tall buildings",
                    "D": "The need for more parks"
                },
                correct_answer="B",
                explanation="The peregrine falcon example is introduced after mentioning 'some species have demonstrated remarkable adaptability to urban environments.'",
                skill_category="inference"
            ),
            ReadingQuestion(
                reading_item_id=medium_passage_1.id,
                question="According to the passage, what type of urban development best supports wildlife?",
                options={
                    "A": "High-rise buildings",
                    "B": "Cities with green infrastructure",
                    "C": "Industrial zones",
                    "D": "Shopping districts"
                },
                correct_answer="B",
                explanation="The passage states that 'Cities that incorporate green infrastructure...tend to support more diverse wildlife populations.'",
                skill_category="detail"
            )
        ]

        for q in questions_medium_1:
            db.add(q)

        # HARD LEVEL PASSAGE
        hard_passage_1 = ReadingItem(
            title="The Quantum Revolution in Computing",
            difficulty="hard",
            skill_tags=["inference", "vocabulary", "synthesis"],
            passage="""Quantum computing represents a paradigm shift in computational technology, leveraging the principles of quantum mechanics to process information in ways that are fundamentally different from classical computers. While classical computers store information in bits that exist in one of two states (0 or 1), quantum computers use quantum bits, or qubits, which can exist in multiple states simultaneously through a phenomenon called superposition. This property, combined with quantum entanglement—where qubits become correlated in ways that have no classical analog—enables quantum computers to perform certain calculations exponentially faster than their classical counterparts.

The implications of quantum computing extend across numerous fields. In cryptography, quantum computers pose both opportunities and threats. Current encryption methods, which rely on the computational difficulty of factoring large numbers, could become vulnerable to quantum attacks. Shor's algorithm, developed by mathematician Peter Shor in 1994, demonstrated that a sufficiently powerful quantum computer could factor large numbers efficiently, potentially rendering current encryption standards obsolete. This has spurred the development of quantum-resistant cryptographic protocols.

However, the practical implementation of quantum computers faces significant challenges. Qubits are extraordinarily fragile and susceptible to decoherence—the loss of their quantum properties due to environmental interference. Maintaining quantum coherence requires isolating qubits at temperatures near absolute zero and minimizing any external disturbances. Current quantum computers are also limited in scale, with the most advanced systems containing only a few hundred qubits, far fewer than would be needed to outperform classical computers on most practical problems.

Despite these challenges, recent progress has been encouraging. In 2019, Google claimed to have achieved "quantum supremacy"—the point at which a quantum computer can perform a calculation that would be practically impossible for a classical computer. While the specific calculation had limited practical application, it demonstrated the potential of quantum technology. Researchers are now focusing on developing quantum error correction techniques and scaling up qubit counts, with some experts predicting that quantum computers could revolutionize drug discovery, materials science, and optimization problems within the next decade.

The quantum revolution also raises philosophical questions about the nature of computation and reality. The success of quantum computing would validate aspects of quantum mechanics that some physicists find conceptually troubling, such as the reality of superposition and entanglement. As quantum computers become more powerful, they may provide new insights into the fundamental laws of physics and the limits of computation itself."""
        )

        db.add(hard_passage_1)
        db.flush()

        questions_hard_1 = [
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="What distinguishes qubits from classical bits?",
                options={
                    "A": "Qubits are faster",
                    "B": "Qubits can exist in multiple states simultaneously",
                    "C": "Qubits are more reliable",
                    "D": "Qubits use less energy"
                },
                correct_answer="B",
                explanation="The passage states that qubits 'can exist in multiple states simultaneously through a phenomenon called superposition,' unlike classical bits.",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="The word 'paradigm' in paragraph 1 is closest in meaning to:",
                options={"A": "model", "B": "problem", "C": "calculation", "D": "experiment"},
                correct_answer="A",
                explanation="'Paradigm' refers to a typical example or pattern, which is closest to 'model' in this context.",
                skill_category="vocabulary"
            ),
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="What can be inferred about current encryption methods?",
                options={
                    "A": "They are already obsolete",
                    "B": "They could be vulnerable to quantum computers",
                    "C": "They will never be broken",
                    "D": "They were designed for quantum computers"
                },
                correct_answer="B",
                explanation="The passage states that current encryption 'could become vulnerable to quantum attacks' and that Shor's algorithm could 'potentially render current encryption standards obsolete.'",
                skill_category="inference"
            ),
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="According to the passage, what is 'decoherence'?",
                options={
                    "A": "The process of creating qubits",
                    "B": "A type of quantum entanglement",
                    "C": "The loss of quantum properties due to interference",
                    "D": "A method of error correction"
                },
                correct_answer="C",
                explanation="The passage defines decoherence as 'the loss of their quantum properties due to environmental interference.'",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="What was significant about Google's 2019 achievement?",
                options={
                    "A": "It solved a major practical problem",
                    "B": "It created the first qubit",
                    "C": "It demonstrated quantum computer potential",
                    "D": "It made quantum computers commercially available"
                },
                correct_answer="C",
                explanation="While the calculation had 'limited practical application,' it 'demonstrated the potential of quantum technology' by achieving quantum supremacy.",
                skill_category="inference"
            ),
            ReadingQuestion(
                reading_item_id=hard_passage_1.id,
                question="The word 'susceptible' in paragraph 3 is closest in meaning to:",
                options={"A": "resistant", "B": "vulnerable", "C": "immune", "D": "related"},
                correct_answer="B",
                explanation="'Susceptible' means likely to be affected by something, which is synonymous with 'vulnerable.'",
                skill_category="vocabulary"
            )
        ]

        for q in questions_hard_1:
            db.add(q)

        # Add more passages (one more for each difficulty)

        easy_passage_2 = ReadingItem(
            title="The Benefits of Regular Exercise",
            difficulty="easy",
            skill_tags=["main-idea", "detail", "vocabulary"],
            passage="""Regular physical exercise is essential for maintaining good health. Health experts recommend at least 150 minutes of moderate exercise or 75 minutes of vigorous exercise per week. Exercise provides numerous benefits for both physical and mental health.

Physical benefits of exercise include stronger muscles and bones, improved cardiovascular health, and better weight management. Regular physical activity helps prevent many chronic diseases such as heart disease, diabetes, and certain types of cancer. It also strengthens the immune system, making the body more resistant to illness.

Mental health benefits are equally important. Exercise releases endorphins, chemicals in the brain that act as natural mood elevators. Many studies have shown that regular physical activity can reduce symptoms of depression and anxiety. Exercise also improves sleep quality and can boost self-esteem and confidence.

You don't need expensive gym equipment to exercise. Simple activities like walking, jogging, swimming, or cycling are excellent forms of exercise. Even household chores like gardening or cleaning can contribute to your daily physical activity. The key is to find activities you enjoy and make them a regular part of your routine."""
        )

        db.add(easy_passage_2)
        db.flush()

        questions_easy_2 = [
            ReadingQuestion(
                reading_item_id=easy_passage_2.id,
                question="How many minutes of moderate exercise do experts recommend per week?",
                options={"A": "75 minutes", "B": "100 minutes", "C": "150 minutes", "D": "200 minutes"},
                correct_answer="C",
                explanation="The passage states 'Health experts recommend at least 150 minutes of moderate exercise.'",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=easy_passage_2.id,
                question="What are endorphins?",
                options={
                    "A": "A type of exercise",
                    "B": "Chemicals that improve mood",
                    "C": "Muscle tissue",
                    "D": "A chronic disease"
                },
                correct_answer="B",
                explanation="The passage describes endorphins as 'chemicals in the brain that act as natural mood elevators.'",
                skill_category="detail"
            ),
            ReadingQuestion(
                reading_item_id=easy_passage_2.id,
                question="The main purpose of this passage is to:",
                options={
                    "A": "Sell gym memberships",
                    "B": "Explain the benefits of exercise",
                    "C": "Describe different sports",
                    "D": "Discuss mental illness"
                },
                correct_answer="B",
                explanation="The passage focuses on explaining both physical and mental benefits of regular exercise.",
                skill_category="main-idea"
            )
        ]

        for q in questions_easy_2:
            db.add(q)

        db.commit()
        print("✅ Successfully seeded reading practice data!")
        print("   - 3 reading passages (easy, medium, hard)")
        print("   - 18 total questions with explanations")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_reading_data()
