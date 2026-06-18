# GEN_MEDICAL_SHEET

Application for generating medical sheets with a PySide6 UI, Mistral chat streaming, audio transcription, and structured transcript extraction.

## Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python3 src/main.py
```

Deactivate the environment:

```bash
deactivate
```

Environment variables

Create a `.env` file in the project root containing your Mistral API key:

```bash
MISTRAL_API_KEY=your_api_key_here
```

## Architecture

The code is split by role.

- `MainWindow` builds the screen.
- Widgets display the interface.
- Controllers coordinate user actions.
- Infrastructure talks to APIs, audio devices, and worker threads.

```text
src/
  main.py
  config/
    constants.py
  domain/
    models/
      message.py
      prompts/
        prompts.py
  application/
    controllers/
      chat_controller.py
      transcription_controller.py
  infrastructure/
    ai/
      mistral_service.py
      transcription_service.py
      transcript_extraction_service.py
    audio/
      audio_recorder_manager.py
    workers/
      mistral_request_thread.py
      transcription_request_thread.py
      transcript_extraction_request_thread.py
  ui/
    main_window.py
    widgets/
    dialogs/
    style/
    assets/
```

### Layer responsibilities

- `ui/`
  - Builds windows, widgets, dialogs, styles, and layouts.
  - Updates labels, buttons, spinners, and chat bubbles.
  - Does not call APIs directly.
  - Does not manage worker threads.

- `application/controllers/`
  - Coordinates workflows.
  - Starts background work.
  - Receives worker results.
  - Emits Qt signals back to the UI.
  - Does not change widgets directly.

- `infrastructure/`
  - Talks to external systems.
  - Contains Mistral API services.
  - Contains audio recording backend code.
  - Contains worker threads.

- `domain/`
  - Contains shared app data.
  - Contains message roles.
  - Contains prompts.

- `config/`
  - Contains constants.
  - Contains resource paths.

### Flow

Chat flow:

```text
User clicks send
-> MainWindow reads input and updates chat UI
-> ChatController starts MistralRequestThread
-> MistralService streams chunks
-> ChatController emits chunks
-> MainWindow appends chunks to ChatWidget
```

Audio flow:

```text
User clicks record
-> MainWindow updates recording button and timer
-> AudioRecorderManager records audio
-> AudioRecorderManager emits recorder events
-> MainWindow starts transcription when recording is finalized
```

Transcription flow:

```text
MainWindow has an audio file
-> TranscriptionController starts TranscriptionRequestThread
-> TranscriptionService transcribes audio
-> MainWindow receives transcript signal
-> TranscriptionController starts extraction
-> TranscriptExtractionService extracts structured data
-> MainWindow receives extraction result
```

## Reference

https://www.freecodecamp.org/news/build-a-local-ai/#heading-local-ai-power-with-qwen-3-and-ollama
