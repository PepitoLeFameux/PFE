import sys
from VideoManager import VideoManager
from api import generate_content

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 1:
        print('=' * 80)
        print('                      VIDEO PROCESSING TOOL')
        print('=' * 80)
        print('\nUSAGE:')
        print('  python main.py <command> [arguments]')
        print('\nCOMMANDS:')
        print('  add_video <video_path>')
        print('      Add a video from the specified path')
        print()
        print('  remove_video <video_idx>')
        print('      Remove video at the specified index')
        print()
        print('  remove_all_videos')
        print('      Remove all videos from the collection')
        print()
        print('  answer_prompt <video_idx> <prompt_type> [custom_prompt]')
        print('      Process a video with a predefined or custom prompt')
        print()
        print('  show_all_videos')
        print('      Show all uploaded videos')
        print()
        print('PROMPT TYPES:')
        print('  SUMMARIZE')
        print('      Summarize the video with general idea and important details')
        print()
        print('  TIMESTAMPS')
        print('      Generate a list of notable events with timestamps')
        print()
        print('  AUDIO_SUMMARY')
        print('      Transcribe the dialogue in the video')
        print()
        print('  AUDIO_TRANSCRIPTION')
        print('      Transcribe the dialogue with timestamps')
        print()
        print('  CUSTOM_PROMPT')
        print('      Use a custom prompt (must provide [custom_prompt] argument)')
        print()
        print('EXAMPLES:')
        print('  python main.py add_video /path/to/video.mp4')
        print('  python main.py remove_video 2')
        print('  python main.py answer_prompt 1 SUMMARIZE')
        print('  python main.py answer_prompt 3 CUSTOM_VIDEO "Describe the people in this video"')
        print()
        print('-' * 80)
    else:
        command = args[0]
        manager = VideoManager()
        if command == 'add_video':
            if len(args) != 2:
                print('Usage: python main.py add_video <video_path>')
                print('Example: python main.py add_video /path/to/video.mp4')
            else:
                video_path = args[1]
                manager.upload_video(video_path)

        elif command == 'remove_video':
            if len(args) != 2:
                print('Usage: python main.py remove_video <video_idx>')
                print('Example: python main.py remove_video 1')
            else:
                video_idx = int(args[1])
                name = manager.get_nth_video_upload_name(video_idx)
                manager.remove_video(name)

        elif command == 'remove_all_videos':
            if len(args) != 1:
                print('Usage: python main.py remove_all_videos')
                print('Note: This command doesn\'t require additional arguments')
            else:
                manager.remove_all_videos()

        elif command == 'answer_prompt':
            if len(args) not in (3, 4):
                print('Usage: python main.py answer_prompt <video_idx> <prompt>')
                print('Example: python main.py answer_prompt 1 "Describe what happens in this video"')
            else:
                video_idx = int(args[1])
                video_upload_name = manager.get_nth_video_upload_name(video_idx)
                task = args[2]  # Join all remaining arguments as the prompt
                upload_name = manager.get_nth_video_upload_name(video_idx)
                if task == 'CUSTOM_PROMPT':
                    custom_prompt = args[3]
                    print(generate_content(video_upload_name, task, custom_prompt=custom_prompt))
                else:
                    print(generate_content(video_upload_name, task))

        elif command == 'show_all_videos':
            if len(args) != 1:
                print('Usage: python main.py show_all_videos')
            else:
                manager.show_all_videos()

        else:
            print(f"Unknown command: {command}")
            print('Usage: python main.py <command> [arguments]')
            print('Run without arguments to see available commands')
