package de.pacheco

import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.net.HttpURLConnection
import java.net.URI
import java.nio.file.Paths
import java.util.concurrent.Executors

import com.github.doyaaaaaken.kotlincsv.dsl.csvReader


@Serializable
data class ScryfallResponse(val image_uris: ImageUris? = null)

@Serializable
data class ImageUris(val png: String)

fun main(args: Array<String>): kotlin.Unit = runBlocking {
    if (args.isEmpty()) {
        println("Bitte gib den Pfad zur CSV-Datei als ersten Parameter an.")
        return@runBlocking
    }

    val csvPath = args[0]
    val outputDir = if (args.size > 1) args[1] else "Bilder"
    val logFile = File("result.log")
    logFile.writeText("Fehlerhafte Einträge:\n")

//    val lines = File(csvPath).readLines().drop(1) // Header ignorieren
    val rows = csvReader().readAll(File(csvPath)).drop(1)
    val outputFolder = File(outputDir)
    outputFolder.mkdirs()

    val dispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

    rows.mapIndexed { index, parts ->
        launch(dispatcher) {
            delay(index * 150L) // Abstand zwischen Requests
//            val parts = line.split(",")
//            if (parts.size < 3) {
//                logFile.appendText("Ungültige Zeile: $line\n")

            if (parts.size < 4) {
                logFile.appendText("Ungültige Zeile: ${parts.joinToString(",")}\n")
                return@launch
            }

            val name = parts[2].trim()
            val id = parts.last().trim()
            val apiUrl = "https://api.scryfall.com/cards/$id"

            try {
                val json = URI(apiUrl).toURL().readText()
//                val json = URL(apiUrl).readText()
                val response = Json { ignoreUnknownKeys = true }.decodeFromString<ScryfallResponse>(json)
                val pngUrl = response.image_uris?.png

                if (pngUrl == null) {
                    logFile.appendText("Kein PNG für $name ($id)\n")
                    return@launch
                }

                val connection = URI(pngUrl).toURL().openConnection() as HttpURLConnection
                connection.inputStream.use { input ->
                    val contentDisposition = connection.getHeaderField("Content-Disposition")
                    val filename = contentDisposition?.let {
                        Regex("filename=\"?([^\";]+)\"?").find(it)?.groupValues?.get(1)
                    } ?: "$name.png"

                    val outputFile = Paths.get(outputFolder.path, filename).toFile()
                    outputFile.outputStream().use { output -> input.copyTo(output) }
                    println("Gespeichert: $filename")
                }
            } catch (e: Exception) {
                logFile.appendText("Fehler bei $name ($id): ${e.message}\n")
            }
        }
    }.joinAll()

    dispatcher.close()
    println("Fertig! Fehler siehe in result.log")
}
