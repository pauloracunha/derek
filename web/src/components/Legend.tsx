// Legenda permanente da codificação visual de incerteza — spec.md FR-007/US4.
// Sempre visível, não depende de seleção de lugar (testável isoladamente).
export default function Legend() {
  return (
    <div className="legend" aria-label="Legenda">
      <h3>Como ler o mapa</h3>
      <ul>
        <li>
          <span className="legend__swatch candidate-marker candidate-marker--point" />
          Círculo cheio = candidato de localização de ponto exato
        </li>
        <li>
          <span className="legend__swatch candidate-marker candidate-marker--area" />
          Losango = candidato de localização de área aproximada (assentamento/região)
        </li>
        <li>Opacidade e tamanho do marcador são proporcionais à probabilidade relativa de cada candidato — nunca mostramos só o candidato mais provável.</li>
        <li>
          <span className="legend__swatch candidate-marker-halo legend__halo" />
          Anel tracejado ao redor do marcador = precisão posicional (precision_meters) — quanto maior o anel, menos preciso o candidato; sem anel = precisão desconhecida.
        </li>
        <li>Linha tracejada conecta candidatos concorrentes do mesmo lugar quando ele está selecionado.</li>
      </ul>
    </div>
  )
}
