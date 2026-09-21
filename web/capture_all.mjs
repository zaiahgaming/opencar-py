import puppeteer from 'puppeteer';

const ARTIFACTS_DIR = '/home/zaiah/.gemini/antigravity-cli/brain/37719168-6265-41c8-b964-41b51fa9d6db';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });

  // 1. Capture Infotainment
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: `${ARTIFACTS_DIR}/real_infotainment.png` });
  console.log('Captured real_infotainment.png');

  // 2. Open Climate Modal and capture
  const climateClicked = await page.evaluate(() => {
    const btn = document.getElementById('appBtn_climate') || document.getElementById('driverTempBtn');
    if (btn) { btn.click(); return true; }
    return false;
  });
  if (climateClicked) {
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: `${ARTIFACTS_DIR}/real_climate_modal.png` });
    console.log('Captured real_climate_modal.png');
  }

  // Reload to reset
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 600));

  // 3. Switch to Cluster / HUD
  const hudBtn = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('nav button'));
    const btn = btns.find(b => b.textContent.includes('Cluster / HUD'));
    if (btn) { btn.click(); return true; }
    return false;
  });
  if (hudBtn) {
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: `${ARTIFACTS_DIR}/real_hud.png` });
    console.log('Captured real_hud.png');
  }

  // 4. Switch to Rear Display
  const rearBtn = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('nav button'));
    const btn = btns.find(b => b.textContent.includes('Rear Display'));
    if (btn) { btn.click(); return true; }
    return false;
  });
  if (rearBtn) {
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: `${ARTIFACTS_DIR}/real_rear.png` });
    console.log('Captured real_rear.png');

    // Click Retro Pong
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('nav button, button'));
      const btn = btns.find(b => b.textContent.includes('Retro Pong') || b.textContent.includes('PLAY RETRO PONG'));
      if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: `${ARTIFACTS_DIR}/real_rear_arcade.png` });
    console.log('Captured real_rear_arcade.png');
  }

  // 5. Switch to Split Cockpit
  const splitBtn = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('nav button'));
    const btn = btns.find(b => b.textContent.includes('Split Cockpit'));
    if (btn) { btn.click(); return true; }
    return false;
  });
  if (splitBtn) {
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: `${ARTIFACTS_DIR}/real_split.png` });
    console.log('Captured real_split.png');
  }

  await browser.close();
  console.log('All screenshots captured successfully!');
})();
