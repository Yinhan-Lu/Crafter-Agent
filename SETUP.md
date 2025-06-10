# Crafter-Agent Project Setup Guide

This guide will help you set up the virtual environment and dependencies for the Crafter-Agent project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Virtual Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Yinhan-Lu/Crafter-Agent
cd Crafter-Agent
```

### 2. Create Virtual Environment

#### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv crafter_env

# Activate virtual environment
# On Windows:
crafter_env\Scripts\activate
# On macOS/Linux:
source crafter_env/bin/activate
```

#### Using conda (Alternative)

```bash
# Create conda environment
conda create -n crafter_env python=3.9
conda activate crafter_env
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

## Environment Configuration

### 1. Create Environment Variables File

```bash
# Copy the template
cp .env.template .env
```

### 2. Configure API Key

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_actual_api_key_here
```

## Project Structure

```
Crafter-Agent/
├── crafter_agents/           # Main project directory
│   ├── agents/              # AI agent implementations
│   ├── game/                # Game state and action space
│   ├── utils/               # Utility functions and helpers
│   ├── planning/            # Planning and task management
│   └── run_agents.py        # Main execution script
├── crafter/                 # Game environment (included)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .env.template           # Template for environment variables
└── README.md               # Project documentation
```

## Running the Project

### 1. Activate Virtual Environment

```bash
# If not already activated
source crafter_env/bin/activate  # macOS/Linux
# or
crafter_env\Scripts\activate     # Windows
```

### 2. Run the Agent

```bash
cd crafter_agents
python run_agents.py
```

### 3. Run Multiple Trajectories

```bash
# The main() function in run_agents.py can be modified to run multiple trajectories
# Example: Run 3 trajectories with 50 steps each
python run_agents.py
```

## Package Dependencies Explained

### Core AI/ML Libraries

- **openai**: Interface with OpenAI's GPT models for agent reasoning
- **numpy**: Numerical computing for game state processing
- **matplotlib**: Plotting and visualization

### Image Processing

- **Pillow (PIL)**: Image manipulation and processing
- **opencv-python**: Computer vision and video recording
- **imageio**: Image I/O operations

### Game Environment

- **pygame**: Game rendering and display
- **ruamel.yaml**: YAML configuration file processing
- **opensimplex**: Procedural noise generation for world generation

### Configuration

- **python-dotenv**: Environment variable management for API keys

### Development Tools (Optional)

- **pytest**: Unit testing framework
- **black**: Code formatting
- **flake8**: Code linting

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Make sure you're in the correct directory
   cd crafter_agents
   # And that your virtual environment is activated
   ```

2. **OpenAI API Key Issues**

   ```bash
   # Check your .env file exists and contains the API key
   cat .env
   ```

3. **Pygame Display Issues on Linux**

   ```bash
   # Install additional dependencies
   sudo apt-get install python3-dev python3-pygame
   ```

4. **macOS Permission Issues**
   ```bash
   # You might need to allow terminal access to screen recording
   # Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   ```

### Virtual Environment Management

#### Deactivate Environment

```bash
deactivate
```

#### Remove Environment

```bash
# If using venv
rm -rf crafter_env

# If using conda
conda env remove -n crafter_env
```

#### Update Dependencies

```bash
# Activate environment first
pip install --upgrade -r requirements.txt
```

## Development Setup

### Additional Development Dependencies

```bash
pip install pytest black flake8 mypy
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black crafter_agents/
```

### Code Linting

```bash
flake8 crafter_agents/
```

## Notes

- The project includes a local `crafter` package for the game environment
- Make sure to keep your `.env` file private and never commit it to version control
- The project generates gameplay videos in MP4 format when recording is enabled
- GPU acceleration is not required but may improve performance for larger models

## Support

If you encounter issues:

1. Check that all dependencies are installed correctly
2. Verify your Python version is 3.8+
3. Ensure your OpenAI API key is valid and has sufficient credits
4. Check the project's GitHub issues for known problems
