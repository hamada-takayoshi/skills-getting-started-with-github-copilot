import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

initial_activities = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


# このテストは、GET /activities がアクティビティ一覧を正しく返すことを検証します
def test_get_activities_returns_all_activities():
    # Arrange
    # すべてのアクティビティ情報を取得するエンドポイントを準備する
    endpoint = "/activities"

    # Act
    # GET リクエストを実行する
    response = client.get(endpoint)

    # Assert
    # 取得した結果が成功で、アクティビティデータに参加者情報が含まれていることを確認する
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert "participants" in body["Chess Club"]


# このテストは、新しい参加者が指定のアクティビティに正常に登録されることを検証します
def test_signup_for_activity_adds_new_participant():
    # Arrange
    # 新しい参加者を特定アクティビティに登録する準備をする
    activity_name = "Chess Club"
    email = "alex@mergington.edu"
    endpoint = f"/activities/{quote(activity_name)}/signup"

    # Act
    # POST リクエストでサインアップを実行する
    response = client.post(endpoint, params={"email": email})

    # Assert
    # 登録が成功し、参加者リストに新しいメールアドレスが追加されていることを確認する
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


# このテストは、既に登録されている参加者を再登録しようとした場合に 400 が返ることを検証します
def test_signup_returns_400_for_duplicate_participant():
    # Arrange
    # 既に登録済みの参加者で重複登録を試みる準備をする
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    endpoint = f"/activities/{quote(activity_name)}/signup"

    # Act
    # 重複登録の POST リクエストを実行する
    response = client.post(endpoint, params={"email": email})

    # Assert
    # 400 エラーが返り、重複登録のエラーメッセージが含まれていることを確認する
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# このテストは、DELETE /activities/{activity_name}/signup で参加者が正常に削除されることを検証します
def test_remove_participant_from_activity():
    # Arrange
    # 既存の参加者をアクティビティから削除する準備をする
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"
    endpoint = f"/activities/{quote(activity_name)}/signup"

    # Act
    # DELETE リクエストで参加者削除を実行する
    response = client.delete(endpoint, params={"email": email})

    # Assert
    # 削除が成功し、対象のメールアドレスが参加者リストから除外されていることを確認する
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


# このテストは、存在しない参加者の削除要求が 404 を返すことを検証します
def test_remove_missing_participant_returns_404():
    # Arrange
    # 存在しない参加者を削除しようとする準備をする
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    endpoint = f"/activities/{quote(activity_name)}/signup"

    # Act
    # DELETE リクエストを実行する
    response = client.delete(endpoint, params={"email": email})

    # Assert
    # 404 エラーが返り、参加者が見つからないことを確認する
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
