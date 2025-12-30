import argparse

parser = argparse.ArgumentParser()

def add_args():
    parser.add_argument('--first_name', 
                        type=str, 
                        help='Name of the user',
                        required=True)

    parser.add_argument('--resume_pdf_path', 
                        type=str,
                        help='Path to resume',
                        default="application_pipeline/application_materials/resume.pdf")

    parser.add_argument('--config_path', 
                        type=str,
                        help='Path to config file',
                        default="config/run_config.json")
    
    parser.add_argument('--cover_letter_path', 
                        type=str,
                        help='Path to cover letter',
                        default="application_pipeline/application_materials/cover_letter.pdf")
    
    parser.add_argument('--applied_path', 
                        type=str,
                        help='Path to applied jobs',
                        default="application_pipeline/application_materials/applied.json")

    parser.add_argument('--mail_protocol', 
                        type=str,
                        help='Mail protocol e.g gmail.com, outlook.com',
                        default="gmail.com")

    # Language variant - now comes from config, but can be overridden
    parser.add_argument('--spell_variant', 
                        type=str,
                        help='Spelling variant: british, american, australian, canadian, etc. (overrides config)',
                        default=None)

    parser.add_argument('--model', 
                        type=str,
                        help='gemini model',
                        default="gemini-2.5-flash")

    parser.add_argument('--min_score', 
                        type=float,
                        help='Min job matching score (set to 0 to disable filtering)',
                        default=0.0)
    
    parser.add_argument('--show_recent_role',
                            type=int,
                            help='Adds recent role to seek job application for employers. 0 = False',
                            default=1)
    
    args = parser.parse_args()
    args.show_recent_role = bool(args.show_recent_role)

    return args
