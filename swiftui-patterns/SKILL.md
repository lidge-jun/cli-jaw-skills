---
name: swiftui-patterns
description: SwiftUI architecture patterns, state management with @Observable, view composition, navigation, performance optimization, and modern iOS/macOS UI best practices.
---

# SwiftUI Patterns

> **Updated for Xcode 26 / iOS 27 (WWDC 2026)**

Modern SwiftUI patterns for building declarative, performant user interfaces on Apple platforms. Covers the Observation framework, view composition, type-safe navigation, persistence with SwiftData, and performance optimization.

## When to Activate

- Building SwiftUI views and managing state (`@State`, `@Observable`, `@Binding`)
- Designing navigation flows with `NavigationStack`
- Structuring view models and data flow
- Optimizing rendering performance for lists and complex layouts
- Working with environment values and dependency injection in SwiftUI

## State Management

### Property Wrapper Selection

Choose the simplest wrapper that fits:

| Wrapper | Use Case |
|---------|----------|
| `@State` | View-local value types (toggles, form fields, sheet presentation) |
| `@Binding` | Two-way reference to parent's `@State` |
| `@Observable` class + `@State` | Owned model with multiple properties |
| `@Observable` class (no wrapper) | Read-only reference passed from parent |
| `@Bindable` | Two-way binding to an `@Observable` property |
| `@Environment` | Shared dependencies injected via `.environment()` |

### @Observable ViewModel

Use `@Observable` (not `ObservableObject`) — it tracks property-level changes so SwiftUI only re-renders views that read the changed property:

```swift
@Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    var searchText = ""

    private let repository: any ItemRepository

    init(repository: any ItemRepository = DefaultItemRepository()) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchAll()) ?? []
    }
}
```

### View Consuming the ViewModel

```swift
struct ItemListView: View {
    @State private var viewModel: ItemListViewModel

    init(viewModel: ItemListViewModel = ItemListViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .searchable(text: $viewModel.searchText)
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```

### Environment Injection

Replace `@EnvironmentObject` with `@Environment`:

```swift
// Inject
ContentView()
    .environment(authManager)

// Consume
struct ProfileView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        Text(auth.currentUser?.name ?? "Guest")
    }
}
```

## View Composition

### Extract Subviews to Limit Invalidation

Break views into small, focused structs. When state changes, only the subview reading that state re-renders:

```swift
struct OrderView: View {
    @State private var viewModel = OrderViewModel()

    var body: some View {
        VStack {
            OrderHeader(title: viewModel.title)
            OrderItemList(items: viewModel.items)
            OrderTotal(total: viewModel.total)
        }
    }
}
```

### ViewModifier for Reusable Styling

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```

### TabView (Updated API)

Use the `Tab` type inside `TabView` for a declarative, type-safe tab bar:

```swift
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }
    Tab("Search", systemImage: "magnifyingglass") {
        SearchView()
    }
    Tab("Profile", systemImage: "person") {
        ProfileView()
    }
}
.tabViewStyle(.tabBarOnly)  // iOS 27+: tab bar without sidebar option
```

For apps with many tabs, use `.sidebarAdaptable` style to allow the tab bar to expand into a sidebar on iPad and Mac.

## Navigation

### Type-Safe NavigationStack

Use `NavigationStack` with `NavigationPath` for programmatic, type-safe routing:

```swift
@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

enum Destination: Hashable {
    case detail(Item.ID)
    case settings
    case profile(User.ID)
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { dest in
                    switch dest {
                    case .detail(let id): ItemDetailView(itemID: id)
                    case .settings: SettingsView()
                    case .profile(let id): ProfileView(userID: id)
                    }
                }
        }
        .environment(router)
    }
}
```

## Performance

### Use Lazy Containers for Large Collections

`LazyVStack` and `LazyHStack` create views only when visible:

```swift
ScrollView {
    LazyVStack(spacing: 8) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### Stable Identifiers

Always use stable, unique IDs in `ForEach` — avoid using array indices:

```swift
// Use Identifiable conformance or explicit id
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}
```

### Avoid Expensive Work in body

- Never perform I/O, network calls, or heavy computation inside `body`
- Use `.task {}` for async work — it cancels automatically when the view disappears
- Use `.sensoryFeedback()` and `.geometryGroup()` sparingly in scroll views
- Minimize `.shadow()`, `.blur()`, and `.mask()` in lists — they trigger offscreen rendering

### Equatable Conformance

For views with expensive bodies, conform to `Equatable` to skip unnecessary re-renders:

```swift
struct ExpensiveChartView: View, Equatable {
    let dataPoints: [DataPoint] // DataPoint must conform to Equatable

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.dataPoints == rhs.dataPoints
    }

    var body: some View {
        // Complex chart rendering
    }
}
```

## Data Persistence with SwiftData

Prefer **SwiftData** over Core Data for new projects. It integrates natively with SwiftUI's observation system:

```swift
@Model
class Task {
    var title: String
    var isCompleted: Bool
    var createdAt: Date

    init(title: String, isCompleted: Bool = false) {
        self.title = title
        self.isCompleted = isCompleted
        self.createdAt = .now
    }
}

struct TaskListView: View {
    @Query(sort: \Task.createdAt, order: .reverse) private var tasks: [Task]
    @Environment(\.modelContext) private var context

    var body: some View {
        List(tasks) { task in
            Text(task.title)
        }
    }
}
```

Use `@Query` for reactive fetching and `@Environment(\.modelContext)` for writes. Configure the model container at the app level with `.modelContainer(for: [Task.self])`.

## Previews

Use `#Preview` macro with inline mock data for fast iteration:

```swift
#Preview("Empty state") {
    ItemListView(viewModel: ItemListViewModel(repository: EmptyMockRepository()))
}

#Preview("Loaded") {
    ItemListView(viewModel: ItemListViewModel(repository: PopulatedMockRepository()))
}
```

## Anti-Patterns to Avoid

- Using `ObservableObject` / `@Published` / `@StateObject` / `@EnvironmentObject` in new code — migrate to `@Observable`
- Putting async work directly in `body` or `init` — use `.task {}` or explicit load methods
- Creating view models as `@State` inside child views that don't own the data — pass from parent instead
- Using `AnyView` type erasure — prefer `@ViewBuilder` or `Group` for conditional views
- Ignoring `Sendable` requirements when passing data to/from actors

## References

See skill: `swift-actor-persistence` for actor-based persistence patterns.
See skill: `swift-protocol-di-testing` for protocol-based DI and testing with Swift Testing.
