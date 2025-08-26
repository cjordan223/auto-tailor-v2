# TexTailor Frontend

A modern, responsive frontend for the TexTailor resume and cover letter generation system.

## Features

### Step-by-Step Configuration Interface

The application now features a streamlined, modern step-by-step configuration interface that guides users through the AI provider setup process:

1. **Provider Selection** - Choose from multiple AI providers (Google Gemini, OpenAI, Mistral, Groq, Ollama)
2. **Model Selection** - Select the specific AI model for your tasks
3. **Personality Selection** - Choose the writing style for your AI assistant
4. **Review & Complete** - Review your configuration and get started

#### Key Improvements

- **Modern UI**: Clean, card-based design with smooth animations and transitions
- **Progressive Disclosure**: Each step focuses on one decision, reducing cognitive load
- **Auto-advance**: Automatically progresses to the next step after selection (with 800ms delay)
- **Visual Feedback**: Progress bar, step indicators, and hover effects
- **Responsive Design**: Works seamlessly on desktop and mobile devices

#### User Experience Features

- **Smooth Transitions**: Fade-in animations between steps
- **Interactive Cards**: Hover effects and visual feedback for selections
- **Progress Tracking**: Clear visual indication of completion status
- **Accessibility**: Proper focus states and keyboard navigation
- **Information Preservation**: All provider details and warnings are maintained

## Development

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

## Architecture

The frontend is built with Vue 3 and uses:

- **Vue 3 Composition API** for reactive state management
- **Tailwind CSS** for styling
- **Vite** for fast development and building
- **Vue Router** for navigation
- **Axios** for API communication

## Components

### ProviderSelector.vue

The main configuration component that implements the step-by-step wizard:

- **Step Management**: Handles progression through configuration steps
- **Provider Data**: Comprehensive provider and model information
- **Auto-advance**: Configurable automatic progression
- **Responsive Design**: Adapts to different screen sizes
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Configuration Options

### AI Providers

- **Google Gemini**: Best balance of speed, quality, and cost (Recommended)
- **OpenAI**: Highest quality, premium pricing
- **Mistral**: High quality, competitive pricing
- **Groq**: Ultra-fast inference, competitive pricing
- **Ollama (Local)**: Free local models, requires setup

### Writing Personalities

- **Career-Savvy Colleague**: Trusted peer providing collaborative, grounded advice (Default)
- **Direct & Confident**: Authoritative, results-focused with measurable outcomes
- **Enthusiastic Innovator**: Forward-thinking, passionate about cutting-edge solutions
- **Calm Mentor**: Wise, experienced guide with stable professionalism
- **Engaging Storyteller**: Witty, narrative-driven approach to showcase experience
- **Meticulous Analyst**: Data-driven, systematic approach with evidence-based claims
- **Ambitious Go-Getter**: High-energy, achievement-focused with urgency for results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.