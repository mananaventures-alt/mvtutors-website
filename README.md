# MV Tutors Website

A Flask-based website for MV Tutors - Expert tutoring services for high school and university students.

## Features

- Responsive design using Tailwind CSS
- Interactive navigation with jQuery
- Hero section with call-to-action buttons
- Services overview section
- How it works process
- Customer testimonials
- About us section with video placeholder
- Pricing packages
- Contact/booking section
- Mobile-friendly navigation

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
MVTutors_Website/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main website template
└── README.md             # This file
```

## Technologies Used

- **Flask**: Python web framework
- **HTML5**: Markup language
- **Tailwind CSS**: Utility-first CSS framework
- **jQuery**: JavaScript library for DOM manipulation
- **Google Fonts**: Inter font family

## Customization

- To modify colors, update the CSS custom properties in the `<style>` section
- To add real images, replace the placeholder divs with `<img>` tags
- To integrate with a booking system, update the button click handlers in the JavaScript section
- To add a contact form, create additional routes in `app.py` and corresponding templates

## Notes

- All images are currently placeholders with colored backgrounds and icons
- Button clicks show alert messages - these should be replaced with actual functionality
- The video section contains a placeholder - integrate with your actual video content
- Navigation uses smooth scrolling to different sections of the single-page application
