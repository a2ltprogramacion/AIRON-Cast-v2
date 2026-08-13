import os
import sys
import datetime

def generate_humans(output_path, components="A2LT Premium Design System"):
    # Values extracted from Argenis' request
    template_vars = {
        "last_update": datetime.date.today().strftime("%Y/%m/%d"),
        "components": components,
        "author_role": "IT Solutions Architect & Engineer",
        "author_link": "https://a2lt.netlify.app/"
    }
    
    # Simple template replacement
    raw_template = """/* TEAM */
    Chef: Argenis León
    Role: {{ author_role }}
    Contact: hola [at] a2lt.solutions
    Twitter: @a2lt_soluciones
    GitHub: https://github.com/a2ltprogramacion/
    From: Venezuela (Remote for the World)

/* THANKS */
    Antigravity AI (The Forge)
    Open Source Community (Astro, Tailwind, Netlify)

/* SITE */
    Last update: {{ last_update }}
    Standards: HTML5, CSS3, JAMstack (Astro + Decap CMS)
    Components: {{ components }}
    Software: Powered by ⚡ A2LT Soluciones ({{ author_link }})
"""
    
    rendered = raw_template
    for key, value in template_vars.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
    except IOError as e:
        print(f"Error writing file {output_path}: {e}")
        sys.exit(1)
        
    print(f"Success: humans.txt generated at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_humans_txt.py <output_path> [components]")
        sys.exit(1)
        
    out_file = sys.argv[1]
    comp = sys.argv[2] if len(sys.argv) > 2 else "A2LT Premium Design System"
    generate_humans(out_file, comp)
