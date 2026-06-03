-- Daily Digest database schema + seed data
-- Compatible with SQLite (recommended for this Flask app)

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS interactions;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    preferences TEXT,
    premium INTEGER NOT NULL DEFAULT 0 CHECK (premium IN (0, 1)),
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
);

CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT 'Daily Digest Editorial',
    image_url TEXT,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    tags TEXT,
    premium INTEGER NOT NULL DEFAULT 0 CHECK (premium IN (0, 1))
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('View', 'Like', 'Bookmark', 'Share')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    UNIQUE(user_id, article_id, type)
);

CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_comments_article_id ON comments(article_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_interactions_article_id ON interactions(article_id);
CREATE INDEX idx_interactions_user_id ON interactions(user_id);
CREATE INDEX idx_interactions_type ON interactions(type);

INSERT INTO users (id, username, email, password, preferences, premium, is_admin) VALUES
(1, 'john_doe', 'john.d@example.com', 'pass123', 'Tech,Sports', 1, 1),
(2, 'jane_smith', 'jane.s@example.com', 'securePass!', 'Politics,Finance', 1, 0),
(3, 'mike_ross', 'mike.r@example.com', 'lawyer123', 'Lifestyle,Travel', 0, 0),
(4, 'sarah_connor', 'sarah.c@example.com', 'skynet00', 'Science,Tech', 1, 0),
(5, 'bruce_wayne', 'b.wayne@example.com', 'batman1', 'Technology,Auto', 1, 0),
(6, 'clark_kent', 'c.kent@example.com', 'superman2', 'Politics,Local', 0, 0),
(7, 'diana_prince', 'd.prince@example.com', 'wonder3', 'History,Travel', 0, 0),
(8, 'tony_stark', 't.stark@example.com', 'ironman4', 'Tech,Engineering', 1, 0),
(9, 'nat_romanoff', 'n.romanoff@example.com', 'widow5', 'Politics,Global', 0, 0),
(10, 'steve_rogers', 's.rogers@example.com', 'cap6', 'History,Local', 0, 0);

INSERT INTO articles (id, title, author, content, category, date, tags, premium) VALUES
(1, 'The Future of AI in Healthcare', 'Daily Digest Editorial', 'Artificial Intelligence is revolutionizing the healthcare sector in ways previously confined to science fiction. From diagnostic imaging algorithms that detect cancers with greater accuracy than experienced radiologists, to predictive models that identify patients at risk before symptoms appear, AI is fundamentally transforming how we deliver and receive medical care.

Hospitals in major urban centers have begun deploying machine learning systems to optimize bed allocation, reduce wait times, and predict equipment failures before they occur. The economic implications are staggering — analysts estimate billions in annual savings across the global healthcare system.

Yet questions remain. Who is liable when an AI misdiagnoses a patient? How do we address the algorithmic biases baked into training data that historically underrepresented minority populations? Researchers and ethicists are racing to develop governance frameworks that keep pace with technological advancement.', 'Technology', '2023-10-01', 'AI,Health,Innovation', 0),
(2, 'Global Markets Rally', 'Daily Digest Editorial', 'Stock markets across the globe saw significant gains today as investor sentiment shifted following a series of positive economic indicators from major economies. The S&P 500 climbed 1.8% while the FTSE 100 posted its strongest single-day performance in three months.

Analysts attributed the rally primarily to better-than-expected employment data out of the United States and signs that supply chain disruptions — which have plagued manufacturers since 2021 — are finally beginning to ease. Technology and energy sectors led the gains.

However, economists warn that persistent inflation data and upcoming central bank decisions on interest rates could quickly reverse the momentum.', 'Finance', '2023-10-02', 'Stocks,Economy,Money', 1),
(3, 'Championship Finals: A Historic Win', 'Daily Digest Editorial', 'The local team secured a stunning victory in last night''s championship finals, defeating the three-time defending champions in a match that will be talked about for generations. A last-minute goal in extra time sent the packed stadium into euphoria.

Coach Maria Fernandez called it ''the culmination of five years of building a culture of resilience.'' Star forward Kai Johnson, who scored the decisive goal, was visibly emotional in the post-match press conference.

The win secures promotion to the top flight for the first time in the club''s 87-year history.', 'Sports', '2023-10-02', 'Football,Championship', 0),
(4, 'New Mars Rover Sends Photos', 'Daily Digest Editorial', 'NASA has released stunning new high-resolution photographs captured by the latest Mars rover, revealing geological formations that scientists say could reshape our understanding of the planet''s ancient history.

The rover, which landed three months ago after a seven-month journey, has already surpassed its primary mission objectives. Its onboard AI navigation system has proven remarkably effective at autonomously selecting scientifically valuable sampling targets.

A sample return mission is now being planned that could bring Martian rock to Earth laboratories within the next decade.', 'Science', '2023-10-03', 'Space,NASA,Mars', 0),
(5, 'Election Results 2024', 'Daily Digest Editorial', 'The polls have closed and the initial count suggests a dramatically close race that may take several days to fully resolve. Early returns show the incumbent holding a narrow lead in key swing districts, but with large urban centers yet to report, analysts are reluctant to call the outcome.

Voter turnout reached record levels in several states, with early estimates suggesting participation exceeded previous cycles by a significant margin.

Both campaigns have deployed legal teams across contested districts, signaling that a protracted post-election period is likely regardless of the final outcome.', 'Politics', '2023-10-04', 'Election,Vote,Gov', 1),
(6, 'Top 10 Travel Destinations', 'Daily Digest Editorial', 'Looking for your next vacation? Here are the destinations that are captivating travelers this season — offering exceptional value, natural beauty, and cultural richness.

Topping the list is the Azores archipelago, Portugal''s volcanic islands in the Atlantic, where hiking, whale watching, and geothermal hot springs converge. Close behind is Plovdiv, Bulgaria — one of Europe''s oldest continuously inhabited cities.

For those seeking long-haul adventure, Kyushu, Japan''s southernmost main island, offers a quieter alternative to the overtouristed Golden Route.', 'Travel', '2023-10-05', 'Travel,Vacation,Guide', 0),
(7, 'Healthy Eating on a Budget', 'Daily Digest Editorial', 'Eating well does not have to be expensive. With a little planning and some knowledge of seasonal produce, most people can dramatically improve their dietary quality without increasing their grocery bills.

The key insight is to shift the protein anchor of meals toward legumes, eggs, and whole grains — foods that deliver superior nutritional density at a fraction of the cost.

Farmers markets, ethnic grocery stores, and buying in bulk for shelf-stable staples round out the strategy.', 'Health', '2023-10-06', 'Food,Diet,Budget', 0),
(8, 'Review: The Newest Smartwatch', 'Daily Digest Editorial', 'We tested the latest wearable tech to see whether the newest generation of smartwatch delivers on its ambitious promises. After two weeks of daily use, the verdict is nuanced: exceptional in some respects, frustrating in others.

The hardware is undeniably impressive. The display is the sharpest we have seen on a wearable, and the health sensors performed with remarkable accuracy.

But battery performance remains the Achilles heel. Despite manufacturer claims of three-day battery life, our testing consistently returned under 36 hours.', 'Technology', '2023-10-07', 'Gadgets,Review', 0),
(9, 'Climate Change Summit Update', 'Daily Digest Editorial', 'World leaders gathered today to discuss accelerated commitments on emissions reductions, with the host nation releasing a surprise proposal that would establish legally binding carbon targets with financial penalties for non-compliance.

Negotiators from developing nations pushed back on what they described as an unequal burden, arguing that historical emitters must provide substantially greater financial support.

Environmental groups staged demonstrations outside the conference center, calling the proposals inadequate.', 'Environment', '2023-10-08', 'Climate,Summit,Global', 1),
(10, 'The Art of Minimalist Living', 'Daily Digest Editorial', 'How decluttering your home can lead to a more focused and intentional life is a question that has moved from the margins of lifestyle culture to the mainstream.

Studies examining the psychological effects of physical environment consistently find that visual clutter increases cortisol levels, fragments attention, and contributes to decision fatigue.

The minimalist approach does not require austere, empty rooms. Rather, it asks a more fundamental question about each possession: does this item actively serve my life?', 'Lifestyle', '2023-10-09', 'Minimalism,Home', 0);

INSERT INTO comments (id, article_id, user_id, content, timestamp) VALUES
(1, 1, 1, 'AI integration in hospitals will reduce diagnosis time significantly.', '2023-10-01 09:10'),
(2, 3, 1, 'That final match completely changed the season narrative.', '2023-10-02 12:30'),
(3, 2, 2, 'Market optimism seems disconnected from inflation data.', '2023-10-02 10:45'),
(4, 5, 2, 'The early vote count trends are unexpected.', '2023-10-04 08:15'),
(5, 6, 3, 'This destination list is practical and realistic.', '2023-10-05 16:00'),
(6, 10, 3, 'Minimalism improves focus and productivity.', '2023-10-09 19:10'),
(7, 4, 4, 'The rover image resolution is impressive.', '2023-10-03 12:20'),
(8, 8, 5, 'Battery performance is still the main concern.', '2023-10-07 14:10'),
(9, 5, 6, 'The policy implications will unfold over months.', '2023-10-04 09:00'),
(10, 6, 7, 'Travel costs are increasing globally.', '2023-10-05 18:40'),
(11, 9, 9, 'The summit commitments need measurable targets.', '2023-10-08 11:00'),
(12, 5, 10, 'Turnout levels were higher than previous elections.', '2023-10-04 10:10');

INSERT INTO interactions (id, user_id, article_id, type) VALUES
(1, 1, 1, 'View'),
(2, 1, 3, 'Like'),
(3, 1, 8, 'Bookmark'),
(4, 2, 2, 'View'),
(5, 2, 5, 'Like'),
(6, 2, 9, 'Share'),
(7, 3, 6, 'View'),
(8, 3, 10, 'Like'),
(9, 4, 1, 'View'),
(10, 4, 4, 'Like'),
(11, 5, 1, 'View'),
(12, 5, 8, 'Like'),
(13, 6, 5, 'View'),
(14, 7, 6, 'Bookmark'),
(15, 8, 1, 'View'),
(16, 8, 4, 'Like'),
(17, 8, 8, 'Share'),
(18, 9, 5, 'View'),
(19, 9, 9, 'Like'),
(20, 10, 5, 'View');
