-- =====================================================
-- CRITICAL: EXECUTE THIS IN SUPABASE SQL EDITOR
-- 35-Parameter System & Advanced KPI Implementation
-- =====================================================

-- Fix the circular dependency between employees and departments
ALTER TABLE public.departments DROP CONSTRAINT IF EXISTS departments_manager_id_fkey;

-- Create the evaluation parameters table
CREATE TABLE IF NOT EXISTS public.evaluation_parameters (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    parameter_id text UNIQUE NOT NULL,
    name text NOT NULL,
    category text NOT NULL,
    definition text NOT NULL,
    relevance_summary text,
    behavioral_anchors jsonb NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Create employee parameter ratings table
CREATE TABLE IF NOT EXISTS public.employee_parameter_ratings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id uuid NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    parameter_id text NOT NULL REFERENCES public.evaluation_parameters(parameter_id),
    rating_value numeric(3,2) NOT NULL CHECK (rating_value >= 1.0 AND rating_value <= 5.0),
    rater_id uuid REFERENCES public.employees(id),
    rater_type text NOT NULL CHECK (rater_type IN ('self', 'manager', 'peer', 'system')),
    evidence_text text,
    confidence_score numeric(3,2) DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    rating_period_start date NOT NULL,
    rating_period_end date NOT NULL,
    review_cycle_id uuid REFERENCES public.performance_review_cycles(id),
    metadata jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    UNIQUE(employee_id, parameter_id, rater_id, rater_type, rating_period_start)
);

-- Create advanced KPI definitions table
CREATE TABLE IF NOT EXISTS public.advanced_kpis (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_code text UNIQUE NOT NULL,
    name text NOT NULL,
    description text,
    formula_expression text NOT NULL,
    parameter_weights jsonb NOT NULL,
    calculation_frequency text DEFAULT 'quarterly',
    target_value numeric,
    unit text DEFAULT 'score',
    is_active boolean DEFAULT true,
    created_by uuid REFERENCES public.users(id),
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Create calculated KPI values table
CREATE TABLE IF NOT EXISTS public.employee_advanced_kpi_values (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id uuid NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    kpi_code text NOT NULL REFERENCES public.advanced_kpis(kpi_code),
    calculated_value numeric(5,2) NOT NULL,
    component_scores jsonb NOT NULL,
    calculation_date timestamp with time zone DEFAULT now(),
    period_start date NOT NULL,
    period_end date NOT NULL,
    confidence_score numeric(3,2) DEFAULT 1.0,
    metadata jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    UNIQUE (employee_id, kpi_code, period_start)
);

-- Create supporting tables
CREATE TABLE IF NOT EXISTS public.parameter_rating_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_parameter_rating_id uuid NOT NULL REFERENCES public.employee_parameter_ratings(id),
    old_rating_value numeric(3,2),
    new_rating_value numeric(3,2),
    change_reason text,
    changed_by uuid REFERENCES public.users(id),
    changed_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.feedback_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id uuid NOT NULL REFERENCES public.employees(id),
    requested_by uuid NOT NULL REFERENCES public.users(id),
    request_type text NOT NULL CHECK (request_type IN ('360', 'peer', 'upward', 'self')),
    parameters_to_rate text[] NOT NULL,
    target_raters uuid[] NOT NULL,
    due_date date NOT NULL,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'expired')),
    instructions text,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    completed_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS public.employee_ai_insights (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id uuid NOT NULL REFERENCES public.employees(id),
    insight_type text NOT NULL,
    insight_data jsonb NOT NULL,
    confidence_score numeric(3,2),
    model_version text,
    generated_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    is_actionable boolean DEFAULT false
);

-- Fix department-employee relationship
ALTER TABLE public.departments 
ADD CONSTRAINT departments_manager_id_fkey 
FOREIGN KEY (manager_id) REFERENCES public.employees(id) 
DEFERRABLE INITIALLY DEFERRED;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_employee_parameter_ratings_employee_parameter 
ON public.employee_parameter_ratings(employee_id, parameter_id);

CREATE INDEX IF NOT EXISTS idx_employee_parameter_ratings_period 
ON public.employee_parameter_ratings(rating_period_start, rating_period_end);

CREATE INDEX IF NOT EXISTS idx_advanced_kpi_values_employee_date 
ON public.employee_advanced_kpi_values(employee_id, calculation_date);

-- Insert all 35 evaluation parameters
INSERT INTO public.evaluation_parameters (parameter_id, name, category, definition, relevance_summary, behavioral_anchors) VALUES 
('COG_01', 'Purpose and Fulfillment', 'COGNITIVE_MOTIVATIONAL', 'The extent to which an employee derives meaning and personal satisfaction from their role.', 'Boosts engagement, resilience, and retention.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Sees the job as just a paycheck.", "Frequently expresses boredom or that their work does not matter.", "Shows little connection to the company mission."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Articulates a clear connection between their daily tasks and a larger purpose.", "Feels energized by their work impact.", "Aligns their personal values with organizational goals."]}]}'),
('COG_02', 'Positive Mindset', 'COGNITIVE_MOTIVATIONAL', 'An optimistic yet realistic outlook focused on opportunities and solutions.', 'Enhances resilience and problem-solving.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Consistently focuses on what could go wrong.", "Views setbacks as permanent failures.", "Often expresses a cynical or defeated attitude."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Acknowledges challenges but focuses on finding solutions.", "Frames setbacks as learning opportunities.", "Maintains a can-do attitude that uplifts the team."]}]}'),
('COG_03', 'Growth Mindset', 'COGNITIVE_MOTIVATIONAL', 'The belief that abilities can be developed through effort and learning.', 'Promotes continuous improvement and resilience.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Avoids new challenges for fear of failure.", "Is defensive when receiving feedback.", "Believes talent and intelligence are static."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Eagerly seeks out challenging assignments.", "Views feedback as a gift for improvement.", "Actively works to develop new skills."]}]}'),
('COG_04', 'Perseverance (Grit)', 'COGNITIVE_MOTIVATIONAL', 'Sustained passion and persistence toward long-term goals.', 'Ensures goal attainment in complex projects.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Gives up easily when faced with obstacles.", "Frequently changes long-term goals.", "Gets distracted from projects that do not yield immediate results."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Stays committed to a project through its entire lifecycle.", "Finds creative ways to overcome roadblocks.", "Maintains high effort despite fatigue or slow progress."]}]}'),
('COG_05', 'Personal Competence (Self-Efficacy)', 'COGNITIVE_MOTIVATIONAL', 'Confidence in ones ability to meet job-related expectations.', 'Drives initiative and effective task execution.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Expresses self-doubt.", "Hesitates to take on new responsibilities.", "Frequently seeks reassurance before proceeding with a task."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Projects confidence.", "Willingly accepts stretch assignments.", "Trusts their own judgment to make decisions and complete work to a high standard."]}]}'),
('COG_06', 'Intrinsic Motivation', 'COGNITIVE_MOTIVATIONAL', 'The internal drive to perform tasks based on inherent satisfaction.', 'Sustains engagement and high-quality work.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Does the bare minimum required.", "Motivated primarily by deadlines or external rewards.", "Shows little passion for the work itself."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Is genuinely passionate about their subject area.", "Works on tasks because they find them interesting.", "Proactively seeks to learn and improve."]}]}'),
('COG_07', 'Creativity', 'COGNITIVE_MOTIVATIONAL', 'The ability to generate novel and useful ideas or solutions.', 'Drives innovation and process improvement.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Prefers to stick to established procedures.", "Struggles to brainstorm new approaches.", "Rarely offers original ideas."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Consistently proposes original solutions.", "Connects seemingly unrelated concepts.", "Challenges the status quo with innovative thinking."]}]}'),
('COG_08', 'Critical Thinking', 'COGNITIVE_MOTIVATIONAL', 'The ability to objectively analyze information, evaluate arguments, and make reasoned judgments.', 'Essential for complex decision-making and strategy.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Accepts information at face value.", "Makes decisions based on gut feelings or incomplete data.", "Struggles to identify logical flaws in arguments."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Deconstructs problems methodically.", "Questions assumptions.", "Builds arguments based on solid evidence and logic."]}]}'),
('COG_09', 'Systems Thinking', 'COGNITIVE_MOTIVATIONAL', 'The ability to see interrelationships and understand how individual actions impact the whole organization.', 'Fosters strategic alignment and holistic solutions.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Focuses only on their immediate tasks.", "Is unaware of how their work affects other departments.", "Makes decisions that create downstream problems."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Understands how their role fits into the larger organizational ecosystem.", "Anticipates the cross-functional impact of decisions.", "Seeks solutions that benefit the entire system."]}]}'),
('COG_31', 'Future Orientation', 'COGNITIVE_MOTIVATIONAL', 'The extent to which an individual thinks about and plans for the long-term future.', 'Crucial for strategic roles, enabling proactive planning and anticipation of market trends.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Is consumed by day-to-day tasks.", "Rarely considers long-term implications.", "Is often surprised by predictable future trends."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Regularly sets and works toward long-term goals.", "Considers the future impact of current decisions.", "Stays informed about industry trends."]}]}'),
('COG_32', 'Strategic Mindset', 'COGNITIVE_MOTIVATIONAL', 'The ability to link daily tasks to the broader organizational strategy and make decisions that support long-term goals.', 'Separates high-potential employees; ensures alignment and resource optimization.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Executes tasks without understanding the why behind them.", "Makes decisions in isolation that may not align with company goals."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Clearly understands and articulates the company strategy.", "Prioritizes work based on strategic importance.", "Makes trade-offs that benefit the big picture."]}]}'),
('COG_33', 'Innovation Implementation', 'COGNITIVE_MOTIVATIONAL', 'The ability to not only generate creative ideas but also to execute them and drive them to completion.', 'Bridges the gap between creativity and tangible business results.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Has many creative ideas but fails to develop or execute them.", "Leaves ideas as abstract concepts."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Takes a novel idea, creates a plan, secures buy-in, navigates obstacles, and successfully implements it to create measurable value."]}]}'),

('SOC_10', 'Managing Emotions (Emotional Regulation)', 'EMOTIONAL_SOCIAL', 'The ability to recognize and regulate emotions in a constructive, professional manner.', 'Maintains composure and rational decision-making.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Reacts impulsively under stress.", "Visibly shows frustration or annoyance.", "Lets negative moods affect their interactions and work quality."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Remains calm and composed during high-pressure situations.", "Acknowledges feelings without being controlled by them.", "Communicates difficult messages with poise."]}]}'),
('SOC_11', 'Emotional Stability', 'EMOTIONAL_SOCIAL', 'The tendency to remain calm and avoid strong negative reactions under stress.', 'Supports consistent performance and stable team dynamics.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Is frequently anxious, moody, or easily irritated by minor stressors.", "Has unpredictable emotional responses."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Is emotionally consistent and predictable.", "Handles stress with an even-keeled temperament.", "Is a calming influence on the team."]}]}'),
('SOC_12', 'Self-Awareness', 'EMOTIONAL_SOCIAL', 'A clear perception of ones own emotions, strengths, weaknesses, and impact.', 'Foundation of emotional intelligence and leadership.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Is unaware of how their behavior affects others.", "Overestimates their abilities.", "Does not recognize their own emotional triggers."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Has an accurate understanding of their strengths and limitations.", "Can identify their emotions as they arise.", "Recognizes their impact on the team morale."]}]}'),
('SOC_13', 'Cognitive Empathy', 'EMOTIONAL_SOCIAL', 'The intellectual ability to understand another persons perspective without sharing their emotions.', 'Improves negotiation, collaboration, and communication.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Struggles to see situations from others points of view.", "Often misinterprets colleagues motivations.", "Gives advice that is not relevant to their situation."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Accurately articulates a colleagues viewpoint even if they disagree with it.", "Anticipates others reactions.", "Tailors communication effectively."]}]}'),
('SOC_14', 'Emotional Reactivity (Affective Empathy)', 'EMOTIONAL_SOCIAL', 'The tendency to resonate with and share the emotional experiences of others.', 'Enhances team cohesion and trust.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Appears detached or indifferent to the emotional states of others.", "Colleagues may perceive them as cold or unapproachable."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Genuinely shares in the team successes and disappointments, creating strong bonds.", "Can be at risk of emotional burnout if not managed."]}]}'),
('SOC_15', 'Social Support', 'EMOTIONAL_SOCIAL', 'The strength and quality of an employees interpersonal support network.', 'Reduces stress and accelerates knowledge sharing.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Works primarily alone.", "Rarely asks for help or offers it.", "Lacks go-to colleagues for advice or support."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Has a wide and reliable network of colleagues to turn to for help.", "Is seen as a supportive and helpful team member.", "Actively builds relationships."]}]}'),
('SOC_16', 'Social Skills', 'EMOTIONAL_SOCIAL', 'Proficiency in building relationships and navigating social situations effectively.', 'Essential for teamwork, leadership, and client relations.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Frequently experiences interpersonal friction.", "Comes across as awkward or abrasive.", "Struggles to build rapport."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Navigates team dynamics smoothly.", "Is persuasive and well-liked.", "Expertly builds and maintains positive professional relationships."]}]}'),
('SOC_17', 'Communication Skills', 'EMOTIONAL_SOCIAL', 'The ability to convey information clearly, concisely, and effectively.', 'Foundational for preventing misunderstandings and ensuring alignment.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Writes confusing emails.", "Is hard to follow in meetings.", "Message is often misunderstood, leading to rework."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Is a clear, articulate speaker and writer.", "Is an active listener who ensures understanding.", "Keeps stakeholders aligned."]}]}'),

('PER_18', 'Adaptability', 'PERFORMANCE_ADAPTABILITY', 'Flexibility in adjusting ones approach in response to changing demands.', 'Critical for performance in dynamic environments.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Resists changes to processes or priorities.", "Complains when asked to deviate from the plan.", "Struggles with ambiguity."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Embraces change with a positive attitude.", "Quickly masters new processes.", "Remains productive even when priorities shift unexpectedly."]}]}'),
('PER_19', 'Learning Agility', 'PERFORMANCE_ADAPTABILITY', 'The ability to learn quickly from experience and apply lessons to new situations.', 'Key predictor of leadership potential.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Tends to repeat past mistakes.", "Struggles to apply feedback in new contexts.", "Is slow to pick up new skills or technologies."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Actively seeks lessons from both successes and failures.", "Quickly applies new knowledge to solve novel problems.", "Is often an early adopter of new skills."]}]}'),
('PER_20', 'Conscientiousness', 'PERFORMANCE_ADAPTABILITY', 'The tendency to be organized, dependable, and self-disciplined.', 'Strongest personality predictor of job performance.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Misses deadlines.", "Produces sloppy or incomplete work.", "Is generally disorganized and unreliable."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Is exceptionally organized and dependable.", "Always meets commitments.", "Consistently produces high-quality, detail-oriented work."]}]}'),
('PER_21', 'Accountability & Ownership', 'PERFORMANCE_ADAPTABILITY', 'Willingness to take personal responsibility for ones actions and outcomes.', 'Builds trust and a high-performance culture.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Makes excuses for missed deadlines or failures.", "Blames others or external factors.", "Avoids taking responsibility for mistakes."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Says I will handle it and does.", "Takes responsibility for errors and focuses on fixing them.", "Is seen by others as highly reliable."]}]}'),
('PER_22', 'Proactivity & Initiative', 'PERFORMANCE_ADAPTABILITY', 'Acting in anticipation of future needs or problems rather than reacting to them.', 'Drives continuous improvement and innovation.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Waits to be told what to do.", "Acts only when a problem becomes urgent.", "Rarely contributes ideas for improvement."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Identifies future opportunities or challenges and acts on them.", "Starts projects without being asked.", "Consistently seeks to make things better."]}]}'),
('PER_23', 'Collaboration & Teamwork', 'PERFORMANCE_ADAPTABILITY', 'The ability to work cooperatively to achieve common team goals.', 'Essential for project success and team harmony.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Prefers to work alone, withholds information.", "Often prioritizes personal goals over the team success, creating friction."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Actively shares knowledge.", "Proactively offers help.", "Builds a sense of we are in this together."]}]}'),
('PER_24', 'Leadership', 'PERFORMANCE_ADAPTABILITY', 'The ability to guide, influence, and motivate others toward a shared vision.', 'Critical for formal managers and informal influencers.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Is unable to rally a team around a goal.", "Provides unclear direction.", "Fails to motivate others."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Inspires commitment and trust.", "Clearly communicates a compelling vision.", "Empowers others to do their best work."]}]}'),

('ETH_25', 'Integrity', 'ETHICAL_MODERN_WORKPLACE', 'Adherence to ethical principles, honesty, and professional standards.', 'Builds trust and an ethical organizational culture.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Bends the rules for personal convenience.", "Is not transparent.", "May stretch the truth, eroding trust."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Consistently does the right thing, even when difficult.", "Is transparent, honest.", "Can be trusted to handle sensitive information appropriately."]}]}'),
('ETH_26', 'Ethical Awareness in Empathy', 'ETHICAL_MODERN_WORKPLACE', 'Guiding empathetic responses with principles of fairness and impartiality.', 'Prevents favoritism and ensures equitable treatment.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Shows empathy only for their in-group or friends.", "Makes biased decisions allocating resources unfairly."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Balances empathy with fairness.", "Considers the needs of all stakeholders equally.", "Makes principled decisions."]}]}'),
('ETH_27', 'Workplace Adaptability (Empathy)', 'ETHICAL_MODERN_WORKPLACE', 'Adjusting ones empathetic style to suit different professional contexts.', 'Ensures effective collaboration across diverse teams.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Uses the same emotional approach with everyone.", "Appears overly familiar with senior leaders or too formal with close peers."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Skilfully adjusts their empathetic response.", "Offers firm but supportive feedback to a direct report.", "Provides data-driven empathy in a client meeting."]}]}'),
('ETH_28', 'Cultural Intelligence (CQ)', 'ETHICAL_MODERN_WORKPLACE', 'The capability to function effectively in culturally diverse settings.', 'Vital for global teams and diverse markets.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Applies their own cultural norms universally.", "Frequently causes misunderstandings with international colleagues.", "Shows little interest in other cultures."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Adjusts their communication style and behavior to respect cultural differences.", "Navigates diverse settings with ease.", "Builds strong cross-cultural relationships."]}]}'),
('ETH_29', 'Digital Literacy', 'ETHICAL_MODERN_WORKPLACE', 'Proficiency in using digital tools to find, evaluate, and create information.', 'Essential for productivity in all modern roles.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Struggles with basic office software.", "Is slow to adopt new technologies.", "Is inefficient in finding information online."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Masters a wide range of digital tools.", "Leverages technology to enhance productivity.", "Can quickly learn new platforms."]}]}'),
('ETH_30', 'Resilience', 'ETHICAL_MODERN_WORKPLACE', 'The capacity to recover quickly from adversity and maintain well-being under pressure.', 'Enables sustained performance through challenges.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Becomes overwhelmed and discouraged by setbacks.", "Dwells on failure and struggling to bounce back."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Views failure as temporary.", "Adapts well to major disruptions.", "Maintains a positive and functional state in the face of adversity."]}]}'),
('ETH_34', 'Well-being & Stress Management', 'ETHICAL_MODERN_WORKPLACE', 'The ability to proactively manage ones physical and mental health, maintain boundaries, and cope effectively with job stress.', 'Prevents burnout, ensures sustainable performance, and contributes to a healthier workplace culture.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Consistently works excessive hours.", "Shows visible signs of stress or exhaustion.", "Does not take adequate time to recharge."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Effectively manages workload.", "Sets healthy boundaries.", "Utilizes vacation time and openly discusses capacity in a professional manner."]}]}'),
('ETH_35', 'Inclusivity', 'ETHICAL_MODERN_WORKPLACE', 'The proactive and deliberate behavior of welcoming, respecting, and valuing diverse perspectives and individuals.', 'Fosters psychological safety, enhances team innovation, and is essential for a healthy, equitable culture.', '{"scale": "1_TO_5", "anchors": [{"rating_value": 1, "level_descriptor": "Low", "indicators": ["Tends to interrupt or dismiss ideas from certain colleagues.", "Defaults to a homogenous in-group.", "Is unaware of unconscious biases."]}, {"rating_value": 5, "level_descriptor": "High", "indicators": ["Actively solicits and amplifies diverse voices.", "Challenges non-inclusive behavior.", "Ensures everyone feels respected and has an opportunity to contribute."]}]}')

ON CONFLICT (parameter_id) DO UPDATE SET
    name = EXCLUDED.name,
    definition = EXCLUDED.definition,
    relevance_summary = EXCLUDED.relevance_summary,
    behavioral_anchors = EXCLUDED.behavioral_anchors,
    updated_at = now();

-- Insert the 3 advanced KPIs
INSERT INTO public.advanced_kpis (kpi_code, name, description, formula_expression, parameter_weights) VALUES 
('FRLP', 'Future-Ready Leadership Potential Index', 'Measures an employees readiness for leadership roles in dynamic environments', 
 '(PER_19 * 0.30) + (COG_32 * 0.25) + (PER_24 * 0.20) + (COG_03 * 0.15) + (PER_18 * 0.10)',
 '{"PER_19": 0.30, "COG_32": 0.25, "PER_24": 0.20, "COG_03": 0.15, "PER_18": 0.10}'),

('IV', 'Innovation Velocity Score', 'Measures the speed and effectiveness of innovation implementation', 
 '(COG_33 * 0.40) + (COG_07 * 0.25) + (PER_22 * 0.20) + (PER_20 * 0.15)',
 '{"COG_33": 0.40, "COG_07": 0.25, "PER_22": 0.20, "PER_20": 0.15}'),

('CHI', 'Collaborative Health & Burnout Index', 'Measures team collaboration health and individual burnout risk', 
 '(ETH_34 * 0.30) + (PER_23 * 0.25) + (SOC_15 * 0.20) + (COG_01 * 0.15) + (SOC_17 * 0.10)',
 '{"ETH_34": 0.30, "PER_23": 0.25, "SOC_15": 0.20, "COG_01": 0.15, "SOC_17": 0.10}')

ON CONFLICT (kpi_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    formula_expression = EXCLUDED.formula_expression,
    parameter_weights = EXCLUDED.parameter_weights,
    updated_at = now();

-- Create KPI calculation function
CREATE OR REPLACE FUNCTION calculate_advanced_kpi(
    p_employee_id uuid,
    p_kpi_code text,
    p_period_start date DEFAULT CURRENT_DATE - INTERVAL '90 days',
    p_period_end date DEFAULT CURRENT_DATE
) RETURNS numeric AS $$
DECLARE
    kpi_record RECORD;
    param_id text;
    param_weight numeric;
    param_value numeric;
    calculated_score numeric := 0;
    total_weight numeric := 0;
    component_scores jsonb := '{}';
BEGIN
    SELECT * INTO kpi_record FROM advanced_kpis WHERE kpi_code = p_kpi_code AND is_active = true;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'KPI code % not found or inactive', p_kpi_code;
    END IF;
    
    FOR param_id, param_weight IN 
        SELECT key, value::numeric 
        FROM jsonb_each_text(kpi_record.parameter_weights)
    LOOP
        SELECT AVG(rating_value) INTO param_value
        FROM employee_parameter_ratings
        WHERE employee_id = p_employee_id 
        AND parameter_id = param_id
        AND rating_period_end BETWEEN p_period_start AND p_period_end;
        
        IF param_value IS NULL THEN
            param_value := 3.0;
        END IF;
        
        calculated_score := calculated_score + (param_value * param_weight);
        total_weight := total_weight + param_weight;
        component_scores := jsonb_set(component_scores, ARRAY[param_id], to_jsonb(param_value));
    END LOOP;
    
    IF total_weight > 0 THEN
        calculated_score := calculated_score / total_weight * 5.0;
    END IF;
    
    INSERT INTO employee_advanced_kpi_values (
        employee_id, kpi_code, calculated_value, component_scores, period_start, period_end
    ) VALUES (
        p_employee_id, p_kpi_code, calculated_score, component_scores, p_period_start, p_period_end
    ) ON CONFLICT (employee_id, kpi_code, period_start) DO UPDATE SET
        calculated_value = EXCLUDED.calculated_value,
        component_scores = EXCLUDED.component_scores,
        calculation_date = now();
    
    RETURN calculated_score;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON public.evaluation_parameters TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.employee_parameter_ratings TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.advanced_kpis TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.employee_advanced_kpi_values TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.feedback_requests TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.employee_ai_insights TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.parameter_rating_history TO anon, authenticated;

GRANT EXECUTE ON FUNCTION calculate_advanced_kpi TO anon, authenticated;

SELECT 'SUCCESS: 35-Parameter System and Advanced KPIs implemented successfully!' as status; 