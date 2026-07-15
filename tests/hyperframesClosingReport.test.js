import { describe, expect, test } from 'vitest';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const compositionPath = resolve(__dirname, '..', 'hyperframes', 'closing-report', 'index.html');
const decisionTreeDeckPath = resolve(
  __dirname,
  '..',
  'hyperframes',
  'closing-report',
  'decision-tree-results.pptx',
);

function readComposition() {
  return readFileSync(compositionPath, 'utf8');
}

describe('closing report HyperFrames composition', () => {
  test('contains the complete closing report structure and key facts', () => {
    const html = readComposition();
    const sceneCount = (html.match(/class="clip"/g) ?? []).length;

    expect(sceneCount).toBeGreaterThanOrEqual(10);
    expect(html).toContain('data-duration="96"');
    expect(html).toContain('1995-2026');
    expect(html).toContain('48');
    expect(html).toContain('16,691');
    expect(html).toContain('問題與目標');
    expect(html).toContain('資料處理成果');
    expect(html).toContain('系統功能成果');
    expect(html).toContain('測試與驗證');
    expect(html).toContain('公開部署');
    expect(html).toContain('目前限制');
    expect(html).toContain('後續延伸');
    expect(html).toContain('https://react-deckgl-project1-kappa.vercel.app/');
  });

  test('contains proposal goal and schedule comparison with completion status', () => {
    const html = readComposition();

    expect(html).toContain('提案目標逐項對照');
    expect(html).toContain('整理乾淨的結構化資料集');
    expect(html).toContain('最大震度決策樹分類模型');
    expect(html).toContain('準確率、各等級命中率與混淆矩陣');
    expect(html).toContain('地圖與圖表輔助呈現');
    expect(html).toContain('06/17');
    expect(html).toContain('首次諮詢：定主題、認識 Codex CLI');
    expect(html).toContain('06/24');
    expect(html).toContain('環境設定＋需求規劃（PRD）');
    expect(html).toContain('07/01');
    expect(html).toContain('資料整理與探索');
    expect(html).toContain('07/08');
    expect(html).toContain('建立模型＋效能評估＋結果整理');
  });

  test('updates proposal results with measured model outcomes and a working deck link', () => {
    const html = readComposition();

    expect(html).toContain('原提案核心成果已補齊');
    expect(html).toContain('時間外推測試準確率為 28.33%');
    expect(html).toContain('震度 7 沒有測試樣本');
    expect(html).toContain('href="./decision-tree-results.pptx"');
    expect(existsSync(decisionTreeDeckPath)).toBe(true);
  });

  test('updates the final proposal schedule milestone with completed model work', () => {
    const html = readComposition();

    expect(html).toContain('更新最終完成狀況');
    expect(html).toContain('決策樹分類模型、時間外推效能評估、混淆矩陣與結果簡報皆已完成');
    expect(html).not.toContain('模型與效能評估列為後續延伸');
  });

  test('shows presenter, course, and date on the opening cover', () => {
    const html = readComposition();

    expect(html).toContain('姓名：彭元懋');
    expect(html).toContain('課程名稱：結構型資料的分析案例');
    expect(html).toContain('日期：2026-07-12');
  });

  test('ends with learned capabilities from the project', () => {
    const html = readComposition();

    expect(html).toContain('這個專案學到的能力');
    expect(html).toContain('資料清理（Python）');
    expect(html).toContain('互動地圖（React＋deck.gl）');
    expect(html).toContain('自動化測試');
    expect(html).toContain('公開部署（Vercel）');
  });

  test('registers GSAP transitions for scenes and card groups', () => {
    const html = readComposition();

    expect(html).toContain('gsap.min.js');
    expect(html).toContain('gsap.timeline({ paused: true })');
    expect(html).toContain('window.__timelines["closing-report"] = tl');
    expect(html).toContain('data-motion="scene"');
    expect(html).toContain('data-motion-group="cards"');
    expect(html).toContain('stagger: 0.08');
    expect(html).toContain('tl.set(scene, { autoAlpha: 1 }');
  });
});
