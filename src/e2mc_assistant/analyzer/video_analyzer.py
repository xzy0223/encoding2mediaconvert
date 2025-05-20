    def _create_analysis_prompt(self, differences: Dict[str, Any]) -> str:
        """
        Create a prompt for Claude 3.5 to analyze video differences.

        Args:
            differences: Dictionary containing differences between videos

        Returns:
            Prompt string for Claude 3.5
        """
        prompt = """
# Video Comparison Analysis

I need you to analyze the differences between two video files. Below is a JSON object containing the differences detected between the videos. Please provide:

1. A summary of the key differences
2. An explanation of what these differences mean in terms of video quality, encoding, and potential issues/difference in various video players
3. Recommendations for addressing any issues or optimizing the videos
4. Any potential causes for these differences (e.g., different encoding settings, transcoding issues)

## Differences JSON:
```json
{diff_json}
```

Please format your response in Markdown format with clear sections and bullet points where appropriate. Focus on the most significant differences that would impact video quality or playback.
Please output English and Chinese version of your response.
""".strip().format(diff_json=json.dumps(differences, indent=2))
        
        return prompt
