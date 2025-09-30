"""
Mental Wellness Document Scraper
Downloads high-quality mental wellness PDFs from reputable sources
"""

import requests
import os
from urllib.parse import urlparse
import time

# Create documents directory
DOCS_DIR = "../documents"
os.makedirs(DOCS_DIR, exist_ok=True)

# High-quality mental wellness document sources
WELLNESS_DOCUMENTS = {
    # WHO Mental Health Resources
    "WHO_Mental_Health_Action_Plan.pdf": "https://apps.who.int/iris/bitstream/handle/10665/89966/9789241506021_eng.pdf",
    
    # NIMH (National Institute of Mental Health) Resources
    "NIMH_Depression_Basics.pdf": "https://www.nimh.nih.gov/health/publications/depression/depression-508_160141.pdf",
    "NIMH_Anxiety_Disorders.pdf": "https://www.nimh.nih.gov/health/publications/anxiety-disorders/anxiety-disorders-508_159169.pdf",
    
    # CDC Mental Health Resources
    "CDC_Mental_Health_Surveillance.pdf": "https://www.cdc.gov/mmwr/volumes/70/su/pdfs/su7001a1-H.pdf",
    
    # American Psychological Association
    "APA_Stress_Management.pdf": "https://www.apa.org/topics/stress/tips",
    
    # Mental Health First Aid Resources
    "Mental_Health_First_Aid_Guide.pdf": "https://www.mentalhealthfirstaid.org/wp-content/uploads/2019/04/algee-action-plan.pdf",
    
    # Mindfulness and Meditation
    "Mindfulness_Based_Stress_Reduction.pdf": "https://palousemindfulness.com/docs/MBSR_workbook.pdf",
    
    # Cognitive Behavioral Therapy Resources  
    "CBT_Self_Help_Guide.pdf": "https://www.cci.health.wa.gov.au/Resources/Looking-After-Yourself/Depression",
    
    # Crisis Prevention and Management
    "Suicide_Prevention_Guidelines.pdf": "https://www.who.int/publications/i/item/preventing-suicide",
    
    # Workplace Mental Health
    "WHO_Workplace_Mental_Health.pdf": "https://apps.who.int/iris/bitstream/handle/10665/42940/9241590173.pdf",
    
    # Sleep and Mental Health
    "Sleep_Mental_Health_Connection.pdf": "https://www.nhlbi.nih.gov/files/docs/public/sleep/healthy_sleep.pdf",
    
    # Trauma and PTSD Resources
    "PTSD_Treatment_Guidelines.pdf": "https://www.ptsd.va.gov/publications/print/handouts/ptsd-treatment-decision-aid.pdf",
    
    # Youth Mental Health
    "Teen_Mental_Health_Guide.pdf": "https://www.samhsa.gov/sites/default/files/programs_campaigns/childrens_mental_health/atod-facts-adolescents.pdf",
    
    # Addiction and Recovery
    "Substance_Abuse_Mental_Health.pdf": "https://store.samhsa.gov/sites/default/files/d7/priv/tip35.pdf",
    
    # Family Mental Health Support
    "Family_Mental_Health_Guide.pdf": "https://www.nami.org/NAMI/media/NAMI-Media/Public%20Policy/HelpingFamiliesInCrisis_Updated.pdf"
}

# Alternative high-quality sources if primary links fail
ALTERNATIVE_SOURCES = {
    "Anxiety_Coping_Strategies.pdf": "https://www.camh.ca/-/media/files/guides-and-publications/anxiety-guide.pdf",
    "Depression_Self_Help.pdf": "https://www.camh.ca/-/media/files/guides-and-publications/depression-guide.pdf",
    "Stress_Management_Techniques.pdf": "https://www.health.harvard.edu/staying-healthy/why-stress-causes-people-to-overeat",
    "Mindfulness_Practice_Guide.pdf": "https://www.mindful.org/meditation/mindfulness-getting-started/",
    "Crisis_Intervention_Manual.pdf": "https://suicidepreventionlifeline.org/wp-content/uploads/2016/08/Lifeline_Crisis-Chat-Manual_Final.pdf",
    "Mental_Health_Myths_Facts.pdf": "https://www.mentalhealth.gov/basics/myths-facts",
    "Emotional_Regulation_Skills.pdf": "https://www.therapistaid.com/worksheets/emotion-regulation-skills.pdf"
}

def download_pdf(url, filename, max_retries=3):
    """Download PDF with error handling and retries"""
    filepath = os.path.join(DOCS_DIR, filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"✅ {filename} already exists")
        return True
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Downloading {filename} (attempt {attempt + 1})...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and len(response.content) < 1000:
                print(f"⚠️  {filename} - Not a valid PDF, skipping")
                return False
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Successfully downloaded {filename} ({len(response.content)} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    
    return False

def create_sample_documents():
    """Create sample mental wellness documents if downloads fail"""
    sample_docs = {
        "Mental_Health_Basics.txt": """
# Mental Health Basics: A Comprehensive Guide

## Introduction
Mental health is a crucial component of overall well-being that affects how we think, feel, and act. It influences how we handle stress, relate to others, and make healthy choices.

## Understanding Mental Health Conditions

### Depression
Depression is more than just feeling sad or going through a rough patch. It's a serious mental health condition that requires understanding and medical care.

**Symptoms:**
- Persistent sad, anxious, or "empty" mood
- Loss of interest or pleasure in activities
- Fatigue and decreased energy
- Difficulty concentrating
- Changes in sleep patterns

**Coping Strategies:**
- Maintain a regular sleep schedule
- Engage in physical activity
- Connect with supportive people
- Practice mindfulness and meditation
- Seek professional help when needed

### Anxiety Disorders
Anxiety disorders are the most common mental health disorders, affecting millions of people worldwide.

**Types of Anxiety:**
- Generalized Anxiety Disorder (GAD)
- Panic Disorder
- Social Anxiety Disorder
- Specific Phobias

**Management Techniques:**
- Deep breathing exercises
- Progressive muscle relaxation
- Cognitive behavioral therapy techniques
- Regular exercise
- Limiting caffeine and alcohol

### Stress Management
Chronic stress can have serious effects on both mental and physical health.

**Stress Reduction Methods:**
- Time management and organization
- Regular physical exercise
- Mindfulness and meditation practices
- Social support systems
- Healthy lifestyle choices

## Crisis Resources
If you or someone you know is in crisis:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

## Building Resilience
- Develop strong relationships
- Accept change as part of life
- Set realistic goals
- Take decisive actions
- Learn from experiences
- Nurture a positive view of yourself
- Keep things in perspective
- Maintain a hopeful outlook
- Take care of yourself

Remember: Seeking help is a sign of strength, not weakness.
        """,
        
        "Mindfulness_Techniques.txt": """
# Mindfulness and Meditation Techniques

## What is Mindfulness?
Mindfulness is the practice of purposeful, non-judgmental awareness of the present moment.

## Basic Techniques

### 1. Breathing Meditation
- Find a comfortable position
- Focus on your breath
- Notice when your mind wanders
- Gently return attention to breathing

### 2. Body Scan
- Start at the top of your head
- Slowly scan down through your body
- Notice sensations without judgment
- Relax each area as you go

### 3. Mindful Walking
- Walk slowly and deliberately
- Pay attention to each step
- Notice the sensation of your feet touching the ground
- Be aware of your surroundings

### 4. 5-4-3-2-1 Grounding Technique
- 5 things you can see
- 4 things you can touch
- 3 things you can hear
- 2 things you can smell
- 1 thing you can taste

## Benefits of Regular Practice
- Reduced stress and anxiety
- Improved focus and concentration
- Better emotional regulation
- Enhanced self-awareness
- Improved sleep quality
        """,
        
        "Crisis_Prevention.txt": """
# Crisis Prevention and Intervention Guide

## Warning Signs to Watch For

### Suicide Risk Factors
- Talking about wanting to die
- Looking for ways to kill oneself
- Talking about feeling hopeless or having no purpose
- Talking about feeling trapped or in unbearable pain
- Talking about being a burden to others
- Increasing use of alcohol or drugs
- Acting anxious, agitated, or reckless
- Sleeping too little or too much
- Withdrawing or feeling isolated
- Showing rage or talking about seeking revenge
- Displaying extreme mood swings

### Immediate Actions
1. Take all threats seriously
2. Stay with the person or ensure they are not alone
3. Remove any means of self-harm
4. Contact emergency services (911) or crisis hotline (988)
5. Listen without judgment
6. Encourage professional help

### Crisis Resources
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911
- SAMHSA National Helpline: 1-800-662-4357

## Supporting Someone in Crisis
- Listen actively and without judgment
- Express care and concern
- Ask directly about suicidal thoughts
- Don't promise to keep secrets about safety
- Stay with them or help them connect to support
- Follow up regularly

## Self-Care for Supporters
Supporting someone in crisis can be emotionally draining:
- Seek support for yourself
- Practice self-care activities
- Know your limits
- Consider professional guidance
        """
    }
    
    for filename, content in sample_docs.items():
        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 Created sample document: {filename}")

def main():
    print("🔄 Starting Mental Wellness Document Collection...")
    print(f"📁 Documents will be saved to: {os.path.abspath(DOCS_DIR)}")
    
    downloaded_count = 0
    total_docs = len(WELLNESS_DOCUMENTS)
    
    # Try to download primary sources
    for filename, url in WELLNESS_DOCUMENTS.items():
        if download_pdf(url, filename):
            downloaded_count += 1
        time.sleep(1)  # Be respectful to servers
    
    # Try alternative sources if we don't have enough documents
    if downloaded_count < 5:
        print("\n🔄 Trying alternative sources...")
        for filename, url in ALTERNATIVE_SOURCES.items():
            if download_pdf(url, filename):
                downloaded_count += 1
            time.sleep(1)
    
    # Create sample documents to ensure we have content
    print("\n📝 Creating sample mental wellness documents...")
    create_sample_documents()
    
    print(f"\n✅ Document collection complete!")
    print(f"📊 Downloaded: {downloaded_count}/{total_docs} PDFs")
    print(f"📁 Documents saved in: {os.path.abspath(DOCS_DIR)}")
    
    # List all files in documents directory
    doc_files = os.listdir(DOCS_DIR)
    print(f"\n📋 Available documents ({len(doc_files)} total):")
    for i, doc in enumerate(doc_files, 1):
        size = os.path.getsize(os.path.join(DOCS_DIR, doc))
        print(f"  {i}. {doc} ({size:,} bytes)")

if __name__ == "__main__":
    main()