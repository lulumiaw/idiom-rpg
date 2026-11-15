# 成語神話卷軸 RPG

兒童成語闖關遊戲：選角色、輸入名字、看開場故事，再挑戰六大仙島 × 20 關，打敗妖怪、蒐集法寶。

## 檔案結構
- `index.html`：遊戲本體（題庫 `idiomDatabase`、故事 `STORY`／`ENDING`、音樂設定 `BGM` 都在 `<script>` 最上方）
- `images/`：`world_map.jpg` 世界總地圖、`chars/` 男女主角、`islands/` 各島背景、`monsters/` 各島魔王、`relics/` 各島法寶
- `audio/`：（需自行建立）放背景音樂 mp3

## 用 GitHub Pages 發布
1. 把 `index.html`、`images/`（和之後的 `audio/`）上傳到 repository 根目錄。
2. Settings → Pages → Source 選 `Deploy from a branch`，Branch 選 `main` / `(root)`。
3. 等一兩分鐘，即可用 `https://你的帳號.github.io/repository名稱/` 開啟。

## 加背景音樂
1. 在根目錄建立 `audio/` 資料夾，放入 mp3（請使用你有權使用的音樂）。
2. 打開 `index.html`，找到 `const BGM={...}`，把檔名填進去，例如：
   `lobby:"world.mp3", boss:"boss.mp3", island3:"fire.mp3"`
   可用鍵：lobby、story、map、battle、boss、ending，以及 island1 ~ island6。留空就不播放。
3. 遊戲內「⚙ 設定」可開關音樂與調整音量。

## 語音朗讀
使用瀏覽器內建的中文語音（優先選台灣國語），不需要額外檔案。各裝置語音品質不同；個別成語的多音字偶爾會唸錯。

## 其他
- 島嶼標籤位置：改 `POS`（[top%, left%]）。
- 擴充題庫：在 `idiomDatabase` 各島陣列後加 `["成語","解釋","造句"],`。
- 進度、角色、名字、設定都存在瀏覽器 localStorage，換裝置或清除資料會重置。
