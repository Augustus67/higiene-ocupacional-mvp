import { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

type TabKey = 'noise' | 'chemicals' | 'vibration' | 'heat';

function App() {
  const [tab, setTab] = useState<TabKey>('noise');

  const [noiseData, setNoiseData] = useState({
    levels: '85,90,88',
    exposure_hours: '8',
    standard: 'ACGIH',
  });

  const [chemicalData, setChemicalData] = useState({
    standard: 'ACGIH',
    items: 'Acetona: 50, 200; Tolueno: 30, 100',
  });

  const [vibrationData, setVibrationData] = useState({
    acceleration: '4.5',
    exposure_hours: '8',
    vibration_type: 'HAND_ARM',
  });

  const [heatData, setHeatData] = useState({
    wbgt: '29',
    workload: 'MODERATE',
  });

  const [noiseResult, setNoiseResult] = useState<any>(null);
  const [chemicalResult, setChemicalResult] = useState<any>(null);
  const [vibrationResult, setVibrationResult] = useState<any>(null);
  const [heatResult, setHeatResult] = useState<any>(null);

  const handleNoiseSubmit = async () => {
    const levels = noiseData.levels
      .split(',')
      .map((value) => Number(value.trim()))
      .filter((value) => !Number.isNaN(value));

    const response = await fetch(`${API_URL}/api/noise/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        levels,
        exposure_hours: Number(noiseData.exposure_hours),
        standard: noiseData.standard,
      }),
    });

    const data = await response.json();
    setNoiseResult(data);
  };

  const handleChemicalSubmit = async () => {
    const parsedItems = chemicalData.items
      .split(';')
      .map((entry) => entry.trim())
      .filter(Boolean)
      .map((entry) => {
        const [substance, values] = entry.split(':');
        const [concentration, limitValue, limitType = 'TWA'] = (values || '')
          .split(',')
          .map((value) => value.trim());

        return {
          substance: substance.trim(),
          concentration: Number(concentration),
          limit_value: Number(limitValue),
          limit_type: limitType,
        };
      });

    const response = await fetch(`${API_URL}/api/chemicals/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items: parsedItems,
        standard: chemicalData.standard,
      }),
    });

    const data = await response.json();
    setChemicalResult(data);
  };

  const handleVibrationSubmit = async () => {
    const response = await fetch(`${API_URL}/api/vibration/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        acceleration: Number(vibrationData.acceleration),
        exposure_hours: Number(vibrationData.exposure_hours),
        vibration_type: vibrationData.vibration_type,
      }),
    });

    const data = await response.json();
    setVibrationResult(data);
  };

  const handleHeatSubmit = async () => {
    const response = await fetch(`${API_URL}/api/heat/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wbgt: Number(heatData.wbgt),
        workload: heatData.workload,
      }),
    });

    const data = await response.json();
    setHeatResult(data);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">MVP</p>
          <h1>Higiene Ocupacional</h1>
        </div>
      </header>

      <nav className="tab-list">
        {['noise', 'chemicals', 'vibration', 'heat'].map((item) => (
          <button
            key={item}
            className={tab === item ? 'tab active' : 'tab'}
            onClick={() => setTab(item as TabKey)}
          >
            {item === 'noise' && 'Ruído'}
            {item === 'chemicals' && 'Químicos'}
            {item === 'vibration' && 'Vibração'}
            {item === 'heat' && 'Calor'}
          </button>
        ))}
      </nav>

      <main className="content">
        {tab === 'noise' && (
          <section className="panel">
            <h2>Cálculo de Ruído</h2>
            <div className="grid two-columns">
              <label>
                Níveis (dB) - separador por vírgula
                <input
                  value={noiseData.levels}
                  onChange={(event) => setNoiseData({ ...noiseData, levels: event.target.value })}
                />
              </label>
              <label>
                Horas de exposição
                <input
                  type="number"
                  value={noiseData.exposure_hours}
                  onChange={(event) => setNoiseData({ ...noiseData, exposure_hours: event.target.value })}
                />
              </label>
            </div>
            <label>
              Norma
              <select
                value={noiseData.standard}
                onChange={(event) => setNoiseData({ ...noiseData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <button className="primary" onClick={handleNoiseSubmit}>Calcular</button>

            {noiseResult && (
              <div className="result-box">
                <p><strong>Norma:</strong> {noiseResult.standard}</p>
                <p><strong>Leq:</strong> {noiseResult.leq} dB</p>
                <p><strong>Dosagem:</strong> {noiseResult.dose_percent}%</p>
                <p><strong>Limite:</strong> {noiseResult.limit_db} dB</p>
                <p><strong>Status:</strong> {noiseResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{noiseResult.interpretation}</p>
              </div>
            )}
          </section>
        )}

        {tab === 'chemicals' && (
          <section className="panel">
            <h2>Cálculo de Químicos</h2>
            <label>
              Norma
              <select
                value={chemicalData.standard}
                onChange={(event) => setChemicalData({ ...chemicalData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <label>
              Itens no formato: "Substância: concentração, limite, tipo"; separados por ponto-e-vírgula
              <textarea
                rows={5}
                value={chemicalData.items}
                onChange={(event) => setChemicalData({ ...chemicalData, items: event.target.value })}
              />
            </label>
            <button className="primary" onClick={handleChemicalSubmit}>Calcular</button>

            {chemicalResult && (
              <div className="result-box">
                <p><strong>Norma:</strong> {chemicalResult.standard}</p>
                <p><strong>Soma de razões:</strong> {chemicalResult.sum_ratio}</p>
                <p><strong>Máxima razão:</strong> {chemicalResult.max_ratio}</p>
                <p><strong>Status:</strong> {chemicalResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <ul>
                  {chemicalResult.details.map((item: any, index: number) => (
                    <li key={`${item.substance}-${index}`}>
                      {item.substance}: razão {item.ratio} ({item.exceeds ? 'acima' : 'dentro'})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {tab === 'vibration' && (
          <section className="panel">
            <h2>Cálculo de Vibração</h2>
            <div className="grid two-columns">
              <label>
                Aceleração (m/s²)
                <input
                  type="number"
                  value={vibrationData.acceleration}
                  onChange={(event) => setVibrationData({ ...vibrationData, acceleration: event.target.value })}
                />
              </label>
              <label>
                Horas de exposição
                <input
                  type="number"
                  value={vibrationData.exposure_hours}
                  onChange={(event) => setVibrationData({ ...vibrationData, exposure_hours: event.target.value })}
                />
              </label>
            </div>
            <label>
              Tipo
              <select
                value={vibrationData.vibration_type}
                onChange={(event) => setVibrationData({ ...vibrationData, vibration_type: event.target.value })}
              >
                <option value="HAND_ARM">Mão-braço</option>
                <option value="WHOLE_BODY">Corpo inteiro</option>
              </select>
            </label>
            <button className="primary" onClick={handleVibrationSubmit}>Calcular</button>

            {vibrationResult && (
              <div className="result-box">
                <p><strong>A8:</strong> {vibrationResult.a8} m/s²</p>
                <p><strong>Limite:</strong> {vibrationResult.limit_value} m/s²</p>
                <p><strong>Status:</strong> {vibrationResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{vibrationResult.interpretation}</p>
              </div>
            )}
          </section>
        )}

        {tab === 'heat' && (
          <section className="panel">
            <h2>Cálculo de Calor</h2>
            <div className="grid two-columns">
              <label>
                WBGT (°C)
                <input
                  type="number"
                  value={heatData.wbgt}
                  onChange={(event) => setHeatData({ ...heatData, wbgt: event.target.value })}
                />
              </label>
              <label>
                Esforço físico
                <select
                  value={heatData.workload}
                  onChange={(event) => setHeatData({ ...heatData, workload: event.target.value })}
                >
                  <option value="LIGHT">Leve</option>
                  <option value="MODERATE">Moderado</option>
                  <option value="HEAVY">Pesado</option>
                  <option value="VERY_HEAVY">Muito pesado</option>
                </select>
              </label>
            </div>
            <button className="primary" onClick={handleHeatSubmit}>Calcular</button>

            {heatResult && (
              <div className="result-box">
                <p><strong>WBGT:</strong> {heatResult.wbgt} °C</p>
                <p><strong>Limite:</strong> {heatResult.allowable_limit} °C</p>
                <p><strong>Status:</strong> {heatResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{heatResult.interpretation}</p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
