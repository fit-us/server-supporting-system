class MarkdownReader:
    @staticmethod
    def read_file(file_path: str) -> str:
        """
        마크다운 파일을 정적으로 읽는 메서드.
        
        :param file_path: 읽을 마크다운 파일의 경로
        :return: 파일 내용 또는 오류 메시지
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: The file at {file_path} was not found."
        except Exception as e:
            return f"Error: {str(e)}"