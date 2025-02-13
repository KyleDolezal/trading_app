import pytest
import getkey
from handle_exit import handle_exit

def mock_getkey():
    pass

def test_handle_exit_quits_on_q(mocker):
    mock_getkey = mocker.patch('handle_exit.getkey')
    mock_getkey.return_value = 'q'
    with pytest.raises(SystemExit):
        handle_exit()
        getkey.getchar = mock_getkey
        assert True

def test_handle_exit_does_not_systemexit(mocker):
    mock_getkey = mocker.patch('handle_exit.getkey')
    mock_getkey.return_value = 'a'
    handle_exit()
    assert True