"""
Seed script for writing practice data (essay prompts)
Run with: python -m database.seed_writing_data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.models.writing import EssayPrompt


def seed_writing_data():
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(EssayPrompt).first()
        if existing:
            print("Essay prompts already exist. Skipping seed.")
            return

        prompts = [
            # EASY PROMPTS
            EssayPrompt(
                title="The Importance of Learning English",
                prompt_text="""Some people believe that learning English is essential in today's world, while others think people should focus on their native language.

To what extent do you agree or disagree with this statement?

Give reasons for your answer and include relevant examples from your own knowledge or experience.""",
                essay_type="opinion",
                difficulty="easy",
                word_count_min=200,
                word_count_max=300,
                time_limit_minutes=40
            ),

            EssayPrompt(
                title="Benefits of Regular Exercise",
                prompt_text="""Many people believe that regular physical exercise is important for health and well-being.

What are the advantages of exercising regularly?

Give reasons for your answer and include relevant examples from your own knowledge or experience.""",
                essay_type="advantages",
                difficulty="easy",
                word_count_min=200,
                word_count_max=300,
                time_limit_minutes=40
            ),

            # MEDIUM PROMPTS
            EssayPrompt(
                title="Technology and Education",
                prompt_text="""Some people think that technology has made learning easier and more accessible, while others believe it has created new problems in education.

Discuss both views and give your own opinion.

Give reasons for your answer and include relevant examples from your own knowledge or experience.""",
                essay_type="discussion",
                difficulty="medium",
                word_count_min=250,
                word_count_max=300,
                time_limit_minutes=40
            ),

            EssayPrompt(
                title="Working from Home",
                prompt_text="""In recent years, more and more people have been working from home instead of going to an office.

What are the advantages and disadvantages of this trend?

Give reasons for your answer and include relevant examples from your own knowledge or experience.""",
                essay_type="advantages_disadvantages",
                difficulty="medium",
                word_count_min=250,
                word_count_max=300,
                time_limit_minutes=40
            ),

            EssayPrompt(
                title="Environmental Protection",
                prompt_text="""Many people believe that protecting the environment is the responsibility of governments and large companies, while others think individuals should take more action.

Discuss both views and give your opinion. What actions can individuals take to help protect the environment?

Give reasons for your answer and include relevant examples from your own knowledge or experience.""",
                essay_type="discussion",
                difficulty="medium",
                word_count_min=250,
                word_count_max=300,
                time_limit_minutes=40
            ),

            # HARD PROMPTS
            EssayPrompt(
                title="Social Media and Society",
                prompt_text="""Social media has fundamentally changed the way people communicate and share information. Some argue that these platforms have democratized information and strengthened communities, while others contend that they have increased misinformation, polarization, and mental health issues.

To what extent do you agree that the benefits of social media outweigh its drawbacks?

Discuss both perspectives and provide your own opinion, supported by relevant examples and evidence.""",
                essay_type="argumentative",
                difficulty="hard",
                word_count_min=250,
                word_count_max=350,
                time_limit_minutes=40
            ),

            EssayPrompt(
                title="Artificial Intelligence in the Workplace",
                prompt_text="""Artificial intelligence and automation are increasingly replacing human workers in various industries. While this technological advancement promises increased efficiency and economic growth, it also raises concerns about unemployment and the changing nature of work.

Evaluate the impact of AI on employment. What measures should society take to address the challenges posed by workplace automation?

Support your answer with relevant examples and evidence from your knowledge or experience.""",
                essay_type="problem_solution",
                difficulty="hard",
                word_count_min=250,
                word_count_max=350,
                time_limit_minutes=40
            ),

            EssayPrompt(
                title="Globalization and Cultural Identity",
                prompt_text="""Globalization has led to increased interconnectedness between countries, resulting in the spread of ideas, culture, and technology. However, critics argue that this process threatens local cultures and traditions, leading to cultural homogenization.

To what extent do you agree that globalization poses a threat to cultural diversity? What can be done to preserve local cultures while embracing global connectivity?

Provide specific examples to support your argument.""",
                essay_type="discussion",
                difficulty="hard",
                word_count_min=250,
                word_count_max=350,
                time_limit_minutes=40
            )
        ]

        for prompt in prompts:
            db.add(prompt)

        db.commit()
        print("✅ Successfully seeded essay prompts!")
        print("   - 8 essay prompts across difficulty levels")
        print("   - Easy: 2 prompts")
        print("   - Medium: 3 prompts")
        print("   - Hard: 3 prompts")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_writing_data()
