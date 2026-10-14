import java.util.*;

public class Timetable {

    static int N, R;
    static int[] color;
    static int[] slotCount;
    static int bestK;
    static int[] bestColor;
    static List<Integer>[] adj;

    static boolean conflictsWith(int u, int c) {
        for (int v : adj[u]) if (color[v] == c) return true;
        return false;
    }

    static void backtrack(Integer[] order, int pos, int used) {
        if (used >= bestK) return;
        if (pos == N) {
            bestK = used;
            bestColor = color.clone();
            return;
        }
        int u = order[pos];
        for (int c = 0; c < used; c++) {
            if (slotCount[c] >= R) continue;
            if (conflictsWith(u, c)) continue;
            color[u] = c;
            slotCount[c]++;
            backtrack(order, pos + 1, used);
            slotCount[c]--;
            color[u] = -1;
        }
        // new slot
        if (used < bestK) {
            color[u] = used;
            slotCount[used]++;
            backtrack(order, pos + 1, used + 1);
            slotCount[used]--;
            color[u] = -1;
        }
    }

    static int[] dsatur() {
        int[] col = new int[N];
        Arrays.fill(col, -1);
        int[] satCount = new int[N];
        boolean[][] satSet = new boolean[N][N + 5];
        int[] slotCnt = new int[N + 5];
        boolean[] used = new boolean[N];

        for (int step = 0; step < N; step++) {
            int u = -1;
            for (int i = 0; i < N; i++) if (col[i] == -1) {
                if (u == -1
                        || satCount[i] > satCount[u]
                        || (satCount[i] == satCount[u] && adj[i].size() > adj[u].size())) {
                    u = i;
                }
            }
            int c = 0;
            while (c < N + 5 && (satSet[u][c] || slotCnt[c] >= R)) c++;
            col[u] = c;
            slotCnt[c]++;
            for (int v : adj[u]) {
                if (col[v] == -1 && !satSet[v][c]) {
                    satSet[v][c] = true;
                    satCount[v]++;
                }
            }
        }
        return col;
    }

    @SuppressWarnings("unchecked")
    public static void main(String[] args) {
        N = args.length > 0 ? Integer.parseInt(args[0]) : 12;
        R = args.length > 1 ? Integer.parseInt(args[1]) : 3;
        double density = args.length > 2 ? Double.parseDouble(args[2]) : 0.25;
        long seed = args.length > 3 ? Long.parseLong(args[3]) : 5;
        Random rnd = new Random(seed);

        adj = new List[N];
        for (int i = 0; i < N; i++) adj[i] = new ArrayList<>();
        for (int i = 0; i < N; i++)
            for (int j = i + 1; j < N; j++)
                if (rnd.nextDouble() < density) {
                    adj[i].add(j);
                    adj[j].add(i);
                }

        int[] greedy = dsatur();
        int greedySlots = 0;
        for (int c : greedy) greedySlots = Math.max(greedySlots, c + 1);
        System.out.println("DSatur greedy slots: " + greedySlots);

        color = new int[N];
        Arrays.fill(color, -1);
        slotCount = new int[N + 1];
        bestK = greedySlots;
        bestColor = null;

        Integer[] order = new Integer[N];
        for (int i = 0; i < N; i++) order[i] = i;
        Arrays.sort(order, (a, b) -> adj[b].size() - adj[a].size());

        backtrack(order, 0, 0);
        System.out.println("Exact slots (proven optimal): " + bestK);

        List<List<Integer>> slots = new ArrayList<>();
        for (int i = 0; i < bestK; i++) slots.add(new ArrayList<>());
        for (int i = 0; i < N; i++) slots.get(bestColor[i]).add(i + 1);
        for (int s = 0; s < bestK; s++) {
            Collections.sort(slots.get(s));
            System.out.println("Slot " + (s + 1) + ": " + slots.get(s));
        }
    }
}