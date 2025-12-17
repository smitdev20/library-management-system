"""
Management command to seed 100 diverse books.
"""
from django.core.management.base import BaseCommand
from apps.books.models import Book
from datetime import date
import random


class Command(BaseCommand):
    help = 'Seed the database with 100 diverse sample books'

    def handle(self, *args, **options):
        self.stdout.write('Seeding 100 books with diverse genres...')

        # Genre-specific book templates
        books_by_genre = {
            'Education': [
                ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Explores the two systems of thinking'),
                ('Educated', 'Tara Westover', 'A memoir about education and self-invention'),
                ('The Innovators', 'Walter Isaacson', 'How a group of hackers changed the world'),
                ('Sapiens', 'Yuval Noah Harari', 'A brief history of humankind'),
                ('How to Read a Book', 'Mortimer Adler', 'The classic guide to intelligent reading'),
                ('The Art of Learning', 'Josh Waitzkin', 'An inner journey to optimal performance'),
                ('Make It Stick', 'Peter Brown', 'The science of successful learning'),
                ('Mindset', 'Carol Dweck', 'The new psychology of success'),
                ('Peak', 'Anders Ericsson', 'Secrets from the new science of expertise'),
                ('Range', 'David Epstein', 'Why generalists triumph in a specialized world'),
            ],
            'Thriller': [
                ('Gone Girl', 'Gillian Flynn', 'A marriage gone terribly wrong'),
                ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'A Swedish thriller mystery'),
                ('The Silent Patient', 'Alex Michaelides', 'A woman shoots her husband and never speaks again'),
                ('The Da Vinci Code', 'Dan Brown', 'A murder inside the Louvre'),
                ('The Girl on the Train', 'Paula Hawkins', 'A psychological thriller about obsession'),
                ('Sharp Objects', 'Gillian Flynn', 'A reporter returns to her hometown'),
                ('Before I Go to Sleep', 'S.J. Watson', 'A woman wakes each day with no memory'),
                ('The Woman in the Window', 'A.J. Finn', 'An agoraphobic woman witnesses a crime'),
                ('Big Little Lies', 'Liane Moriarty', 'Three women in an affluent beachside town'),
                ('The Snowman', 'Jo Nesbø', 'A detective hunts a serial killer'),
            ],
            'Fiction': [
                ('The Great Gatsby', 'F. Scott Fitzgerald', 'A novel about the American Dream'),
                ('To Kill a Mockingbird', 'Harper Lee', 'A classic about racial injustice'),
                ('Pride and Prejudice', 'Jane Austen', 'A romantic novel of manners'),
                ('The Catcher in the Rye', 'J.D. Salinger', 'Following Holden Caulfield'),
                ('One Hundred Years of Solitude', 'Gabriel García Márquez', 'The Buendía family saga'),
                ('Crime and Punishment', 'Fyodor Dostoevsky', 'A psychological novel about guilt'),
                ('The Kite Runner', 'Khaled Hosseini', 'A story of friendship and redemption'),
                ('The Book Thief', 'Markus Zusak', 'Set in Nazi Germany'),
                ('Life of Pi', 'Yann Martel', 'A boy survives 227 days at sea'),
                ('The Alchemist', 'Paulo Coelho', 'A shepherd journey to find treasure'),
            ],
            'Science Fiction': [
                ('1984', 'George Orwell', 'A dystopian novel about totalitarianism'),
                ('Brave New World', 'Aldous Huxley', 'A futuristic World State'),
                ('Dune', 'Frank Herbert', 'A science fiction epic about desert planet Arrakis'),
                ('The Martian', 'Andy Weir', 'An astronaut stranded on Mars'),
                ('Foundation', 'Isaac Asimov', 'The collapse of the Galactic Empire'),
                ('Neuromancer', 'William Gibson', 'A cyberpunk masterpiece'),
                ('Snow Crash', 'Neal Stephenson', 'Virtual reality and pizza delivery'),
                ('Ender Game', 'Orson Scott Card', 'A child genius military strategy'),
                ('The Hitchhiker Guide to the Galaxy', 'Douglas Adams', 'Comedic space opera'),
                ('Ready Player One', 'Ernest Cline', 'Virtual reality treasure hunt'),
            ],
            'Fantasy': [
                ('The Hobbit', 'J.R.R. Tolkien', 'Bilbo Baggins adventure'),
                ('The Lord of the Rings', 'J.R.R. Tolkien', 'The quest to destroy the One Ring'),
                ('Harry Potter and the Philosopher Stone', 'J.K. Rowling', 'A boy wizard discovers his destiny'),
                ('The Name of the Wind', 'Patrick Rothfuss', 'The legend of Kvothe'),
                ('A Game of Thrones', 'George R.R. Martin', 'Houses vie for the Iron Throne'),
                ('The Way of Kings', 'Brandon Sanderson', 'Epic fantasy on Roshar'),
                ('Mistborn', 'Brandon Sanderson', 'A world ruled by an immortal emperor'),
                ('The Eye of the World', 'Robert Jordan', 'First book of Wheel of Time'),
                ('The Lies of Locke Lamora', 'Scott Lynch', 'A fantasy heist story'),
                ('American Gods', 'Neil Gaiman', 'Old gods meet new in America'),
            ],
            'Mystery': [
                ('The Hound of the Baskervilles', 'Arthur Conan Doyle', 'Sherlock Holmes classic'),
                ('And Then There Were None', 'Agatha Christie', 'Ten strangers on an island'),
                ('The Murder on the Orient Express', 'Agatha Christie', 'Murder on a luxury train'),
                ('The Big Sleep', 'Raymond Chandler', 'Philip Marlowe investigation'),
                ('The Maltese Falcon', 'Dashiell Hammett', 'Sam Spade classic noir'),
                ('In the Woods', 'Tana French', 'A detective haunted by past'),
                ('The No. 1 Ladies Detective Agency', 'Alexander McCall Smith', 'Botswana detective'),
                ('The Moonstone', 'Wilkie Collins', 'First modern English detective novel'),
                ('Devil in a Blue Dress', 'Walter Mosley', 'Easy Rawlins debut'),
                ('Gorky Park', 'Martin Cruz Smith', 'Moscow detective thriller'),
            ],
            'Romance': [
                ('Pride and Prejudice', 'Jane Austen', 'Elizabeth and Mr. Darcy'),
                ('Jane Eyre', 'Charlotte Brontë', 'Governess falls for mysterious employer'),
                ('Wuthering Heights', 'Emily Brontë', 'Passionate and destructive love'),
                ('The Notebook', 'Nicholas Sparks', 'A love that transcends time'),
                ('Outlander', 'Diana Gabaldon', 'Time travel romance'),
                ('Me Before You', 'Jojo Moyes', 'A life-changing relationship'),
                ('The Time Traveler Wife', 'Audrey Niffenegger', 'Love across time'),
                ('The Fault in Our Stars', 'John Green', 'Two teens with cancer'),
                ('Call Me by Your Name', 'André Aciman', 'Summer romance in Italy'),
                ('Normal People', 'Sally Rooney', 'Complicated relationship'),
            ],
            'Horror': [
                ('Dracula', 'Bram Stoker', 'The classic vampire novel'),
                ('Frankenstein', 'Mary Shelley', 'The modern Prometheus'),
                ('The Shining', 'Stephen King', 'Isolation and madness in hotel'),
                ('It', 'Stephen King', 'A shape-shifting evil entity'),
                ('The Haunting of Hill House', 'Shirley Jackson', 'Classic ghost story'),
                ('Pet Sematary', 'Stephen King', 'Sometimes dead is better'),
                ('The Exorcist', 'William Peter Blatty', 'Demonic possession'),
                ('House of Leaves', 'Mark Z. Danielewski', 'Experimental horror'),
                ('Bird Box', 'Josh Malerman', 'Must not see the creatures'),
                ('The Silence of the Lambs', 'Thomas Harris', 'FBI trainee and cannibal'),
            ],
            'Biography': [
                ('Steve Jobs', 'Walter Isaacson', 'The exclusive biography'),
                ('Long Walk to Freedom', 'Nelson Mandela', 'Autobiography of Mandela'),
                ('The Diary of a Young Girl', 'Anne Frank', 'A Jewish girl in hiding'),
                ('Born a Crime', 'Trevor Noah', 'Growing up in apartheid South Africa'),
                ('Becoming', 'Michelle Obama', 'Memoir of former First Lady'),
                ('Einstein: His Life and Universe', 'Walter Isaacson', 'Biography of Einstein'),
                ('The Autobiography of Malcolm X', 'Malcolm X', 'Civil rights leader story'),
                ('Unbroken', 'Laura Hillenbrand', 'WWII survival story'),
                ('When Breath Becomes Air', 'Paul Kalanithi', 'A neurosurgeon facing death'),
                ('Wild', 'Cheryl Strayed', 'A journey of self-discovery'),
            ],
            'Self-Help': [
                ('Atomic Habits', 'James Clear', 'Tiny changes remarkable results'),
                ('The 7 Habits of Highly Effective People', 'Stephen Covey', 'Principles for success'),
                ('How to Win Friends', 'Dale Carnegie', 'Influence people'),
                ('Man Search for Meaning', 'Viktor Frankl', 'Finding purpose in suffering'),
                ('The Power of Now', 'Eckhart Tolle', 'Spiritual enlightenment'),
                ('You Are a Badass', 'Jen Sincero', 'How to stop doubting'),
                ('The Subtle Art of Not Giving', 'Mark Manson', 'Counterintuitive approach'),
                ('Daring Greatly', 'Brené Brown', 'The power of vulnerability'),
                ('The Four Agreements', 'Don Miguel Ruiz', 'Practical guide to freedom'),
                ('Grit', 'Angela Duckworth', 'Power of passion and perseverance'),
            ],
        }

        created_count = 0
        book_counter = 1

        for genre, books in books_by_genre.items():
            for title, author, description in books:
                isbn = f'978{random.randint(1000000000, 9999999999)}'
                page_count = random.randint(200, 600)
                year = random.randint(1900, 2024)
                month = random.randint(1, 12)
                day = random.randint(1, 28)

                book, created = Book.objects.get_or_create(
                    title=title,
                    author=author,
                    defaults={
                        'isbn': isbn,
                        'description': description,
                        'page_count': page_count,
                        'genre': genre,
                        'published_date': date(year, month, day),
                        'is_available': True,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(f'  [{book_counter}/100] Created: {title} ({genre})')
                else:
                    self.stdout.write(f'  [{book_counter}/100] Exists: {title}')

                book_counter += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete! {created_count} new books created across {len(books_by_genre)} genres.'
        ))
