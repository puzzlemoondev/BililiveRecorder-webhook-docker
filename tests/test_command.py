import shutil
import subprocess
from pathlib import Path

import pytest

from webhook.command import Command, CloudStorageCommand

BIN_PATH = Path("/usr/local/bin")


@pytest.fixture(autouse=True)
def mock_shutil(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: str(BIN_PATH.joinpath(cmd)))


@pytest.fixture(autouse=True)
def mock_subprocess(monkeypatch):
    def mock_check_output(cmd, **kwargs):
        assert kwargs == dict(encoding="utf8")
        return cmd

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)


class TestCommand:
    @pytest.fixture
    def command(self, faker):
        command_name = faker.file_path(absolute=False)
        command = Command(command_name)
        assert command.executable == BIN_PATH.joinpath(command_name)
        return command

    def test_call(self, command, faker):
        input_args = ["a", "b", "c"]
        cmd = command(*input_args)

        assert cmd == [command.executable, *input_args]


class TestCloudStorageCommand(TestCommand):
    @pytest.fixture
    def command(self, faker):
        command_name = faker.file_path(absolute=False)
        command = CloudStorageCommand(command_name)
        assert command.executable == BIN_PATH.joinpath(command_name)
        return command

    def test_upload(self, command, faker):
        local_path = faker.file_path()
        remote_path = faker.file_path()
        cmd = command.upload(local_path, remote_path)
        assert cmd == [command.executable, "upload", local_path, remote_path]

    def test_login(self, command, faker):
        credential = faker.uuid4()
        cmd = command.login(credential)
        assert cmd == [command.executable, "login", credential]

    def test_loglist(self, command, faker):
        cmd = command.loglist()
        assert cmd == [command.executable, "loglist"]

    def test_ls(self, command, faker):
        path = faker.file_path(extension="")
        cmd = command.ls(path)
        assert cmd == [command.executable, "ls", path]

    def test_has_account(self, mock_command_loglist, mock_account_count):
        result = mock_command_loglist.has_account()
        assert result == bool(mock_account_count)

    @pytest.fixture(params=range(10))
    def mock_account_count(self, request):
        return request.param

    @pytest.fixture
    def mock_command_loglist(self, mock_account_count, command, faker, monkeypatch):
        def mock_loglist():
            if not mock_account_count:
                return "Name,\r\n"
            return faker.csv(header=("Name",), data_columns=("{{name}}",), num_rows=mock_account_count)

        monkeypatch.setattr(command, "loglist", mock_loglist)
        return command
