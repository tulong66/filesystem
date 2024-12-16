import unittest
import asyncio
from unittest.mock import patch, mock_open, AsyncMock
from filesystem.server import handle_call_tool, handle_list_resources
from pydantic import AnyUrl

class TestFilesystemServer(unittest.IsolatedAsyncioTestCase):

    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    async def test_read_file(self, mock_file):
        """
        Test read_file tool
        """
        result = await handle_call_tool("read_file", {"path": "test.txt"})
        self.assertEqual(result[0].text, "file content")

    @patch('builtins.open', new_callable=mock_open)
    async def test_write_file(self, mock_file):
        await handle_call_tool("write_file", {"path": "test.txt", "content": "new content"})
        mock_file.assert_called_with("test.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_with("new content")

    @patch('os.makedirs')
    async def test_create_directory(self, mock_makedirs):
        await handle_call_tool("create_directory", {"path": "test_dir"})
        mock_makedirs.assert_called_with("test_dir", exist_ok=True)

    @patch('os.listdir')
    @patch('os.path.isfile', return_value=True)
    async def test_list_directory(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ["file1.txt", "file2.txt"]
        result = await handle_call_tool("list_directory", {"path": "test_dir"})
        self.assertEqual(result[0].text, "[FILE] file1.txt\n[FILE] file2.txt")

    @patch('shutil.move')
    async def test_move_file(self, mock_move):
        await handle_call_tool("move_file", {"source": "test.txt", "destination": "test_dir"})
        mock_move.assert_called_with("test.txt", "test_dir")

    @patch('os.walk')
    async def test_search_files(self, mock_walk):
        mock_walk.return_value = [
            ("/test_dir", [], ["file1.txt", "file2.txt"]),
        ]
        result = await handle_call_tool("search_files", {"path": "/test_dir", "pattern": "*.txt"})
        self.assertEqual(result[0].text, "/test_dir/file1.txt\n/test_dir/file2.txt")

    @patch('os.stat')
    async def test_get_file_info(self, mock_stat):
        mock_stat.return_value.st_size = 1024
        mock_stat.return_value.st_ctime = 1609459200
        mock_stat.return_value.st_mtime = 1609545600
        mock_stat.return_value.st_atime = 1609632000
        mock_stat.return_value.st_mode = 33188
        result = await handle_call_tool("get_file_info", {"path": "test.txt"})
        expected_info = {
            "size": 1024,
            "creation_time": 1609459200,
            "modified_time": 1609545600,
            "access_time": 1609632000,
            "type": "file",
            "permissions": "644",
        }
        self.assertEqual(result[0].text, str(expected_info))

    @patch('os.listdir')
    @patch('os.path.isfile', return_value=True)
    async def test_list_directory(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ["file1.txt", "file2.txt"]
        result = await handle_call_tool("list_directory", {"path": "test_dir"})
        self.assertEqual(result[0].text, "[FILE] file1.txt\n[FILE] file2.txt")

    @patch('os.walk')
    async def test_search_files(self, mock_walk):
        mock_walk.return_value = [
            ("/test_dir", [], ["file1.txt", "file2.txt"]),
        ]
        result = await handle_call_tool("search_files", {"path": "/test_dir", "pattern": "*.txt"})
        self.assertEqual(result[0].text, "/test_dir/file1.txt\n/test_dir/file2.txt")

    @patch('os.stat')
    async def test_get_file_info(self, mock_stat):
        mock_stat.return_value.st_size = 1024
        mock_stat.return_value.st_ctime = 1609459200
        mock_stat.return_value.st_mtime = 1609545600
        mock_stat.return_value.st_atime = 1609632000
        mock_stat.return_value.st_mode = 33188
        result = await handle_call_tool("get_file_info", {"path": "test.txt"})
        expected_info = {
            "size": 1024,
            "creation_time": 1609459200,
            "modified_time": 1609545600,
            "access_time": 1609632000,
            "type": "file",
            "permissions": "644",
        }
        self.assertEqual(result[0].text, str(expected_info))

    async def test_handle_list_resources(self):
        """
        Test handle_list_resources function
        """
        result = await handle_list_resources()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].uri, AnyUrl("file://system"))
        self.assertEqual(result[0].name, "File System Operations")
        self.assertEqual(result[0].description, "Interface for file system operations")
        self.assertEqual(result[0].mimeType, "application/json")

if __name__ == '__main__':
    unittest.main()
