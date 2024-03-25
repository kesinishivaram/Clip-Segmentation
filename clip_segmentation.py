import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial

class VideoSegmentationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Segmentation Tool")

        self.video_path = None

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.select_button = tk.Button(self.frame, text="Select Video", command=self.select_video)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.process_button = tk.Button(self.frame, text="Process Video", command=self.process_video, state=tk.DISABLED)
        self.process_button.grid(row=0, column=1, padx=5, pady=5)

    def select_video(self):
        try:
            self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
            if self.video_path:
                self.process_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while selecting the video: {str(e)}")


    def process_video(self):
        if self.video_path:
            try:
                self.segment_video()
                messagebox.showinfo("Success", "Video segmentation completed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def segment_video(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open video file.")

        # Initialize variables
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        prev_frame = None
        shot_boundaries = []

        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to grayscale for simplicity
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect shot boundaries based on frame difference
            if prev_frame is not None:
                frame_diff = cv2.absdiff(gray_frame, prev_frame)
                if cv2.countNonZero(frame_diff) > 10000:  # Adjust threshold as needed
                    shot_boundaries.append(i)

            prev_frame = gray_frame

        # Extract segments based on shot boundaries and filter out small segments
        segments = []
        min_segment_length = 10  # Minimum length of a segment (in frames)
        prev_boundary = 0
        for boundary in shot_boundaries:
            if boundary - prev_boundary >= min_segment_length:
                segments.append((prev_boundary, boundary))
            prev_boundary = boundary

        if frame_count - prev_boundary >= min_segment_length:
            segments.append((prev_boundary, frame_count))

        # Save segments as individual clips (for demonstration purposes)
        for idx, (start, end) in enumerate(segments):
            cap.set(cv2.CAP_PROP_POS_FRAMES, start)
            segment_frames = []
            for i in range(start, end):
                ret, frame = cap.read()
                if not ret:
                    break
                segment_frames.append(frame)

            # Write segment frames to a new video file (for demonstration purposes)
            out = cv2.VideoWriter(f"segment_{idx}.avi", cv2.VideoWriter_fourcc(*'DIVX'), 30, (frame.shape[1], frame.shape[0]))
            for frame in segment_frames:
                out.write(frame)
            out.release()

        cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSegmentationTool(root)
    root.mainloop()
