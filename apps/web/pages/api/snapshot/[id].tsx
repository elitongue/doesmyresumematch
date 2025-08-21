import type { NextApiRequest, NextApiResponse } from 'next';
import { Document, Page, Text, View, StyleSheet, pdf } from '@react-pdf/renderer';
import type {
  ClusterAlignment,
  GapItem,
  ScoreResponse,
  SkillItem,
} from '@doesmyresumematch/shared';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

const styles = StyleSheet.create({
  page: { padding: 24, fontSize: 12, fontFamily: 'Helvetica' },
  section: { marginBottom: 12 },
  heading: { fontSize: 14, marginBottom: 4 },
  barBg: { width: '100%', height: 8, backgroundColor: '#eee', marginTop: 2 },
  bar: { height: 8, backgroundColor: '#3b82f6' },
  listItem: { marginBottom: 2 },
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { id } = req.query;
  if (req.method !== 'GET') {
    res.status(405).end();
    return;
  }
  try {
    const r = await fetch(`${API_BASE}/v1/snapshot/${id}`);
    if (!r.ok) {
      res.status(500).end();
      return;
    }
    const data = (await r.json()) as ScoreResponse;

    const doc = (
      <Document>
        <Page size="A4" style={styles.page}>
          <View style={styles.section}>
            <Text style={styles.heading}>Score</Text>
            <Text>
              {data.score} ({data.label})
            </Text>
          </View>
          <View style={styles.section}>
            <Text style={styles.heading}>Cluster alignment</Text>
            {data.clusters?.map((c: ClusterAlignment) => (
              <View key={c.cluster} style={{ marginBottom: 4 }}>
                <Text>{c.cluster}</Text>
                <View style={styles.barBg}>
                  <View style={[styles.bar, { width: `${c.align_pct}%` }]} />
                </View>
              </View>
            ))}
          </View>
          <View style={styles.section}>
            <Text style={styles.heading}>Best-fit skills</Text>
            {data.best_fit?.map((b: SkillItem, i: number) => (
              <Text key={i} style={styles.listItem}>
                {b.skill}
              </Text>
            ))}
          </View>
          <View style={styles.section}>
            <Text style={styles.heading}>Gaps</Text>
            {data.gaps?.map((g: GapItem, i: number) => (
              <Text key={i} style={styles.listItem}>
                {g.skill}
              </Text>
            ))}
          </View>
          {data.rewrites && data.rewrites.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.heading}>Rewrites</Text>
              {data.rewrites.map((r: string, i: number) => (
                <Text key={i} style={styles.listItem}>
                  • {r}
                </Text>
              ))}
            </View>
          )}
        </Page>
      </Document>
    );

    const buffer = await pdf(doc).toBuffer();
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader(
      'Content-Disposition',
      `attachment; filename=doesmyresumematch-${id}.pdf`
    );
    res.send(Buffer.from(buffer));
  } catch (e) {
    res.status(500).json({ error: 'failed to generate pdf' });
  }
}
